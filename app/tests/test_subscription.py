import pytest
from app.models.subscription import Subscription, Status
from app.models.plan import Plan
from app import db

def auth_header(token):
    return {"Authorization": f"Bearer {token}"}


def test_subscribe_success(client, user_and_token, plan):
    user, token = user_and_token

    payload = {
        "plan_id": plan.id,
        "frequency": "monthly"
    }

    res = client.post(
        "/subscription/subscribe",
        json=payload,
        headers=auth_header(token)
    )
    
    assert res.status_code == 201
    data = res.get_json()
    assert data["plan_id"] == plan.id
    assert data["user_id"] == user.id
    assert data["status"] == Status.active.value


def test_subscribe_with_active_subscription(client, user_and_token, plan):
    user, token = user_and_token

    # Create active subscription
    sub = Subscription(user_id=user.id, plan_id=plan.id,
                       frequency="monthly", amount=100,
                       status=Status.active)
    db.session.add(sub)
    db.session.commit()

    res = client.post("subscription/subscribe", json={
        "plan_id": plan.id,
        "frequency": "monthly"
    }, headers=auth_header(token))

    assert res.status_code == 400
    assert "active subscription" in res.get_json()["error"].lower()


def test_upgrade_subscription_success(client, user_and_token, plan):
    user, token = user_and_token

    old_plan = Plan(name="Starter", price=5.0)
    db.session.add(old_plan)
    db.session.commit()

    sub = Subscription(user_id=user.id, plan_id=old_plan.id,
                       frequency="monthly", amount=60,
                       status=Status.active)
    db.session.add(sub)
    db.session.commit()

    res = client.post("subscription/upgrade", json={
        "plan_id": plan.id,
        "frequency": "monthly"
    }, headers=auth_header(token))

    assert res.status_code == 201
    data = res.get_json()
    assert data["plan_id"] == plan.id
    assert data["user_id"] == user.id
    assert data["status"] == Status.active.value


def test_upgrade_without_active_subscription(client, user_and_token, plan):
    user, token = user_and_token

    res = client.post("subscription/upgrade", json={
        "plan_id": plan.id,
        "frequency": "monthly"
    }, headers=auth_header(token))

    assert res.status_code == 400
    assert "do not have active subscription" in res.get_json()["error"].lower()


def test_cancel_subscription_success(client, user_and_token, plan):
    user, token = user_and_token

    sub = Subscription(user_id=user.id, plan_id=plan.id,
                       frequency="monthly", amount=10.0,
                       status=Status.active)
    db.session.add(sub)
    db.session.commit()

    res = client.patch("subscription/cancel", json={
        "subscription_id": sub.id
    }, headers=auth_header(token))

    assert res.status_code == 200
    assert "Subscription cancelled" in res.get_json()["error"]


def test_cancel_subscription_not_found(client, user_and_token):
    user, token = user_and_token
    res = client.patch("subscription/cancel", json={
        "subscription_id": 9999
    }, headers=auth_header(token))

    assert res.status_code == 404
    assert "Subscription not found or not active" in res.get_json()["error"]