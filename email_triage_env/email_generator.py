"""
Generates realistic email data for the Email Triage environment.
Creates diverse emails with ground truth labels for grading.
"""

import random
from datetime import datetime, timedelta
from typing import List, Tuple
import uuid

from .models import Email, EmailCategory, EmailPriority


# Realistic email templates
EMAIL_TEMPLATES = {
    EmailCategory.WORK: [
        {
            "senders": [
                ("john.smith@company.com", "John Smith"),
                ("sarah.jones@company.com", "Sarah Jones"),
                ("mike.wilson@client.com", "Mike Wilson"),
                ("hr@company.com", "HR Department"),
                ("cto@company.com", "CTO Office"),
            ],
            "subjects": [
                "Q4 Project Update Required",
                "Meeting Tomorrow at 3pm",
                "Review needed: Technical specification",
                "Team standup notes",
                "Performance review scheduling",
                "Budget approval needed",
                "Client feedback on proposal",
            ],
            "bodies": [
                "Hi,\n\nCould you please review the attached document and provide your feedback by EOD? The client is expecting our response tomorrow.\n\nThanks,\n{sender}",
                "Hello team,\n\nJust a reminder about our meeting tomorrow. Please come prepared with your weekly updates.\n\nBest,\n{sender}",
                "Hi,\n\nI've completed the initial draft of the technical specification. When you have a moment, please take a look and let me know if any changes are needed.\n\nRegards,\n{sender}",
                "Team,\n\nAttached are the notes from today's standup. Action items are highlighted.\n\nThanks,\n{sender}",
            ],
            "priorities": [EmailPriority.HIGH, EmailPriority.NORMAL, EmailPriority.NORMAL],
            "requires_response": [True, True, True, False],
        },
    ],
    EmailCategory.PERSONAL: [
        {
            "senders": [
                ("mom@gmail.com", "Mom"),
                ("bestfriend@yahoo.com", "Alex"),
                ("college_buddy@hotmail.com", "Chris"),
                ("neighbor@gmail.com", "Dave"),
            ],
            "subjects": [
                "Dinner this weekend?",
                "Check out these photos!",
                "Happy Birthday!",
                "Long time no see",
                "Recipe you asked for",
            ],
            "bodies": [
                "Hey!\n\nAre you free this weekend? Would love to catch up over dinner.\n\nLet me know!\n{sender}",
                "Hi!\n\nJust wanted to share some photos from the trip. Hope you enjoy them!\n\nMiss you,\n{sender}",
                "Happy Birthday! Hope you have an amazing day filled with joy and celebration!\n\nLove,\n{sender}",
            ],
            "priorities": [EmailPriority.NORMAL, EmailPriority.LOW, EmailPriority.LOW],
            "requires_response": [True, False, True],
        },
    ],
    EmailCategory.SPAM: [
        {
            "senders": [
                ("winner@lottery-intl.com", "Lottery Winner"),
                ("prince@nigeria-royal.net", "Prince Abdullah"),
                ("no-reply@free-iphone.xyz", "Prize Center"),
                ("hot-deals@super-savings.biz", "Amazing Deals"),
                ("crypto@moon-coins.io", "Crypto Guru"),
            ],
            "subjects": [
                "YOU WON $1,000,000!!!",
                "Urgent: Your inheritance awaits",
                "FREE iPhone 15 - Claim NOW!",
                "Make $10,000/day from home",
                "Bitcoin secret revealed",
                "URGENT: Account suspended",
            ],
            "bodies": [
                "CONGRATULATIONS!\n\nYou have been selected as our lucky winner! To claim your prize of $1,000,000, simply reply with your bank details.\n\nAct now before it's too late!",
                "Dear Friend,\n\nI am Prince Abdullah from Nigeria. I have $50 million that I need help transferring. You will receive 30% for your assistance.\n\nPlease respond urgently.",
                "You have been selected to receive a FREE iPhone 15! Click the link below to claim your prize:\n\nhttp://totally-not-spam.xyz/claim",
            ],
            "priorities": [EmailPriority.LOW],
            "requires_response": [False],
            "is_spam": True,
        },
    ],
    EmailCategory.NEWSLETTER: [
        {
            "senders": [
                ("newsletter@techcrunch.com", "TechCrunch"),
                ("digest@medium.com", "Medium Daily Digest"),
                ("weekly@producthunt.com", "Product Hunt"),
                ("news@nytimes.com", "NY Times"),
            ],
            "subjects": [
                "This week in tech",
                "Your daily digest",
                "Top products this week",
                "Morning Briefing",
                "Weekly roundup",
            ],
            "bodies": [
                "Here's what you missed this week in tech:\n\n1. AI breakthrough announced\n2. New startup raises $100M\n3. Tech layoffs continue\n\nRead more on our website.",
                "Good morning!\n\nHere are today's top stories curated just for you.\n\n[Article 1]\n[Article 2]\n[Article 3]\n\nHappy reading!",
            ],
            "priorities": [EmailPriority.LOW],
            "requires_response": [False],
        },
    ],
    EmailCategory.SUPPORT: [
        {
            "senders": [
                ("support@aws.amazon.com", "AWS Support"),
                ("noreply@github.com", "GitHub"),
                ("support@stripe.com", "Stripe Support"),
                ("help@vercel.com", "Vercel Support"),
            ],
            "subjects": [
                "Your support ticket #12345",
                "Action required: Verify your account",
                "Your request has been received",
                "Important security update",
                "Your subscription is expiring",
            ],
            "bodies": [
                "Hello,\n\nThank you for contacting support. Your ticket #12345 has been received and will be reviewed within 24 hours.\n\nBest,\nSupport Team",
                "Hi,\n\nWe noticed unusual activity on your account. Please verify your identity by clicking the secure link below.\n\nIf this wasn't you, please contact us immediately.",
                "Your subscription will expire in 7 days. To continue uninterrupted service, please update your payment method.\n\nThank you for being a valued customer.",
            ],
            "priorities": [EmailPriority.HIGH, EmailPriority.URGENT, EmailPriority.NORMAL],
            "requires_response": [False, True, True],
        },
    ],
    EmailCategory.BILLING: [
        {
            "senders": [
                ("billing@company.com", "Billing Department"),
                ("invoices@vendor.com", "Vendor Invoicing"),
                ("noreply@paypal.com", "PayPal"),
                ("receipts@stripe.com", "Stripe"),
            ],
            "subjects": [
                "Invoice #INV-2024-001",
                "Payment received - Thank you",
                "Your receipt from purchase",
                "Payment failed - Action required",
                "Expense report approval needed",
            ],
            "bodies": [
                "Please find attached your invoice for this month's services.\n\nAmount due: $1,234.56\nDue date: {due_date}\n\nThank you for your business.",
                "We've received your payment of $500.00.\n\nTransaction ID: TXN-12345\nDate: {date}\n\nThank you!",
                "URGENT: Your payment method has failed. Please update your billing information to avoid service interruption.\n\nClick here to update.",
            ],
            "priorities": [EmailPriority.NORMAL, EmailPriority.LOW, EmailPriority.URGENT],
            "requires_response": [False, False, True],
        },
    ],
}

# Urgent email scenarios
URGENT_SCENARIOS = [
    {
        "sender": ("ceo@company.com", "CEO"),
        "subject": "URGENT: Board meeting in 1 hour",
        "body": "I need the quarterly report immediately. The board is waiting.\n\nPlease send ASAP.",
        "category": EmailCategory.WORK,
        "priority": EmailPriority.URGENT,
        "requires_response": True,
    },
    {
        "sender": ("security@bank.com", "Bank Security"),
        "subject": "URGENT: Suspicious activity detected",
        "body": "We've detected unusual activity on your account. Please verify your recent transactions immediately.\n\nCall us at 1-800-XXX-XXXX if you don't recognize this activity.",
        "category": EmailCategory.SUPPORT,
        "priority": EmailPriority.URGENT,
        "requires_response": True,
    },
    {
        "sender": ("oncall@company.com", "On-Call Alert"),
        "subject": "CRITICAL: Production server down",
        "body": "Alert: Production server is unresponsive.\n\nService: API Gateway\nStatus: DOWN\nTime: {time}\n\nImmediate action required.",
        "category": EmailCategory.WORK,
        "priority": EmailPriority.URGENT,
        "requires_response": True,
    },
]


def generate_timestamp(hours_ago: int = 0) -> str:
    """Generate an ISO timestamp for a given number of hours ago."""
    dt = datetime.now() - timedelta(hours=hours_ago)
    return dt.isoformat()


def generate_email(
    category: EmailCategory,
    is_urgent: bool = False,
    hours_ago: int = 0,
) -> Email:
    """Generate a single realistic email with ground truth labels."""
    
    if is_urgent:
        scenario = random.choice(URGENT_SCENARIOS)
        sender_email, sender_name = scenario["sender"]
        return Email(
            id=str(uuid.uuid4()),
            sender=sender_email,
            sender_name=sender_name,
            subject=scenario["subject"],
            body=scenario["body"].format(time=datetime.now().strftime("%H:%M")),
            timestamp=generate_timestamp(hours_ago),
            is_read=False,
            is_flagged=False,
            category=None,
            priority=None,
            requires_response=scenario["requires_response"],
            _true_category=scenario["category"],
            _true_priority=scenario["priority"],
            _is_spam=False,
            _requires_urgent_action=True,
        )
    
    templates = EMAIL_TEMPLATES.get(category, EMAIL_TEMPLATES[EmailCategory.WORK])[0]
    
    sender_email, sender_name = random.choice(templates["senders"])
    subject = random.choice(templates["subjects"])
    body = random.choice(templates["bodies"]).format(
        sender=sender_name,
        due_date=(datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
        date=datetime.now().strftime("%Y-%m-%d"),
    )
    priority = random.choice(templates["priorities"])
    requires_response = random.choice(templates["requires_response"])
    is_spam = templates.get("is_spam", False)
    
    return Email(
        id=str(uuid.uuid4()),
        sender=sender_email,
        sender_name=sender_name,
        subject=subject,
        body=body,
        timestamp=generate_timestamp(hours_ago),
        is_read=False,
        is_flagged=False,
        category=None,
        priority=None,
        requires_response=requires_response if not is_spam else False,
        _true_category=category,
        _true_priority=priority,
        _is_spam=is_spam,
        _requires_urgent_action=priority == EmailPriority.URGENT,
    )


def generate_email_batch(
    num_emails: int,
    spam_ratio: float = 0.15,
    urgent_ratio: float = 0.1,
    category_distribution: dict = None,
) -> List[Email]:
    """
    Generate a batch of emails with specified distribution.
    
    Args:
        num_emails: Total number of emails to generate
        spam_ratio: Proportion of spam emails (0.0 to 1.0)
        urgent_ratio: Proportion of urgent emails (0.0 to 1.0)
        category_distribution: Optional dict mapping categories to proportions
    
    Returns:
        List of generated Email objects
    """
    if category_distribution is None:
        category_distribution = {
            EmailCategory.WORK: 0.35,
            EmailCategory.PERSONAL: 0.15,
            EmailCategory.SPAM: spam_ratio,
            EmailCategory.NEWSLETTER: 0.15,
            EmailCategory.SUPPORT: 0.10,
            EmailCategory.BILLING: 0.10,
        }
    
    emails = []
    num_urgent = int(num_emails * urgent_ratio)
    num_spam = int(num_emails * spam_ratio)
    
    # Generate urgent emails
    for i in range(num_urgent):
        emails.append(generate_email(
            EmailCategory.WORK,
            is_urgent=True,
            hours_ago=random.randint(0, 2),
        ))
    
    # Generate spam emails
    for i in range(num_spam):
        emails.append(generate_email(
            EmailCategory.SPAM,
            hours_ago=random.randint(0, 48),
        ))
    
    # Generate remaining emails based on distribution
    remaining = num_emails - num_urgent - num_spam
    categories = [c for c in EmailCategory if c != EmailCategory.SPAM]
    weights = [category_distribution.get(c, 0.2) for c in categories]
    
    for i in range(remaining):
        category = random.choices(categories, weights=weights)[0]
        emails.append(generate_email(
            category,
            hours_ago=random.randint(0, 72),
        ))
    
    # Shuffle emails
    random.shuffle(emails)
    
    return emails


def generate_task_emails(task_id: str, difficulty: str) -> List[Email]:
    """Generate emails for a specific task based on difficulty."""
    
    if difficulty == "easy":
        # Easy: 5 emails, clear categories, no spam
        return generate_email_batch(
            num_emails=5,
            spam_ratio=0.0,
            urgent_ratio=0.0,
            category_distribution={
                EmailCategory.WORK: 0.4,
                EmailCategory.PERSONAL: 0.3,
                EmailCategory.NEWSLETTER: 0.3,
            },
        )
    
    elif difficulty == "medium":
        # Medium: 10 emails, some spam, one urgent
        return generate_email_batch(
            num_emails=10,
            spam_ratio=0.2,
            urgent_ratio=0.1,
        )
    
    else:  # hard
        # Hard: 20 emails, more spam, multiple urgent, tricky cases
        return generate_email_batch(
            num_emails=20,
            spam_ratio=0.25,
            urgent_ratio=0.15,
        )
