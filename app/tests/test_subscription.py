import pytest
from datetime import datetime, timedelta
from app.models.subscription import Subscription, Status
from app.models.plan import Plan
from app import db
from app.utils.time_util import utc_now

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
    assert data["plan"]['name'] == plan.name
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
    assert "you still have an active subscription" in res.get_json()["error"].lower()


def test_upgrade_subscription_success(client, user_and_token, plan):
    user, token = user_and_token
    now = utc_now()

    old_plan = Plan(name="Starter", price=5.00)
    db.session.add(old_plan)
    db.session.commit()

    sub = Subscription(user_id=user.id, plan_id=old_plan.id,
                       frequency="monthly", amount=60.00,
                       status=Status.active, started_at=now, ended_at=now + timedelta(days=30))
    db.session.add(sub)
    db.session.commit()

    res = client.post("subscription/upgrade", json={
        "plan_id": plan.id,
        "frequency": "monthly"
    }, headers=auth_header(token))

    assert res.status_code == 201
    data = res.get_json()
    assert data["plan"]['name'] == plan.name
    assert data["user_id"] == user.id
    assert data["status"] == Status.active.value


def test_upgrade_without_active_subscription(client, user_and_token, plan):
    user, token = user_and_token

    res = client.post("subscription/upgrade", json={
        "plan_id": plan.id,
        "frequency": "monthly"
    }, headers=auth_header(token))

    assert res.status_code == 400
    assert "you do not have active subscription" in res.get_json()["error"].lower()


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
    assert "Subscription cancelled" in res.get_json()["message"]


def test_cancel_subscription_not_found(client, user_and_token):
    user, token = user_and_token
    res = client.patch("subscription/cancel", json={
        "subscription_id": 9999
    }, headers=auth_header(token))

    assert res.status_code == 404
    assert "Subscription not found or not active" in res.get_json()["error"]
    

def test_list_subscriptions_with_pagination_and_filter(client, user_and_token, plan):
    user, token = user_and_token

    now = datetime.utcnow()

    active_sub = Subscription(
        user_id=user.id,
        plan_id=plan.id,
        frequency='monthly',
        amount=plan.price,
        status='active',
        started_at=now,
        ended_at=now + timedelta(days=30)
    )
    cancelled_sub = Subscription(
        user_id=user.id,
        plan_id=plan.id,
        frequency='yearly',
        amount=plan.price,
        status='cancelled',
        started_at=now - timedelta(days=60),
        ended_at=now - timedelta(days=1)
    )

    db.session.add_all([active_sub, cancelled_sub])
    db.session.commit()

    # Test filtering
    res = client.get(
        "/subscription/?status=active&page=1&per_page=5",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 200
    data = res.get_json()
    
    assert "items" in data
    assert isinstance(data["items"], list)
    assert len(data["items"]) <= 5
    assert "total" in data
    assert "pages" in data
    
    for item in data["items"]:
        assert item["status"] == "active"


def test_retrieve_subscription_success(client, user_and_token, plan):
    user, token = user_and_token
    now = utc_now()

    # Create a subscription
    sub = Subscription(
        user=user,
        plan=plan,
        frequency='monthly',
        amount=plan.price,
        status='active',
        started_at=now,
        ended_at=now + timedelta(days=30)
    )
    db.session.add(sub)
    db.session.commit()

    res = client.get(
        f"/subscription/{sub.id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert res.status_code == 200
    data = res.get_json()
    assert data["user_id"] == user.id
    assert data["id"] == sub.id
    assert data["status"] == "active"
