# Phishing email templates (for phishing detection task)
PHISHING_EMAILS = [
    {
        "sender": ("security@bank-alerts.com", "Bank Security"),
        "subject": "URGENT: Account Locked - Immediate Action Required",
        "body": "Dear Customer,\n\nWe have detected suspicious activity on your account. Please verify your identity by clicking the link below:\n\nhttp://fake-bank-login.com\n\nFailure to do so will result in permanent account suspension.\n\nSincerely,\nBank Security Team",
    },
    {
        "sender": ("it-admin@company-support.com", "IT Admin"),
        "subject": "Password Expiry Notification",
        "body": "Your password will expire in 24 hours. Please reset it immediately using the following link:\n\nhttp://malicious-reset.com\n\nIf you do not act, you will lose access to your account.",
    },
    {
        "sender": ("hr@company.com", "HR Department"),
        "subject": "Unusual Payroll Activity",
        "body": "We noticed unusual activity in your payroll account. Please confirm your details here:\n\nhttp://phishing-hr.com\n\nContact HR if you have questions.",
    },
]
def generate_phishing_email(hours_ago: int = 0) -> Email:
    """Generate a realistic phishing email."""
    template = random.choice(PHISHING_EMAILS)
    sender_email, sender_name = template["sender"]
    return Email(
        id=str(uuid.uuid4()),
        sender=sender_email,
        sender_name=sender_name,
        subject=template["subject"],
        body=template["body"],
        timestamp=generate_timestamp(hours_ago),
        is_read=False,
        is_flagged=False,
        category=None,
        priority=EmailPriority.HIGH,
        requires_response=False,
        _true_category=EmailCategory.WORK,  # Or another relevant category
        _true_priority=EmailPriority.HIGH,
        _is_spam=True,
        _is_phishing=True,
        _requires_urgent_action=False,
    )
"""
Generates realistic email data for the Email Triage environment.
"""

import random
from datetime import datetime, timedelta
from typing import List
import uuid

from .models import Email, EmailCategory, EmailPriority


# =============================================================================
# EMAIL TEMPLATES
# =============================================================================

EMAIL_TEMPLATES = {
    EmailCategory.WORK: [
        {
            "senders": [
                ("john.smith@company.com", "John Smith"),
                ("sarah.jones@company.com", "Sarah Jones"),
                ("mike.wilson@client.com", "Mike Wilson"),
                ("hr@company.com", "HR Department"),
                ("cto@company.com", "CTO Office"),
                ("project.manager@company.com", "Project Manager"),
                ("engineering@company.com", "Engineering Team"),
            ],
            "subjects": [
                "Q4 Project Update Required",
                "Meeting Tomorrow at 3pm",
                "Review needed: Technical specification",
                "Team standup notes",
                "Performance review scheduling",
                "Budget approval needed",
                "Client feedback on proposal",
                "Weekly status report",
                "Code review request",
                "Sprint planning reminder",
            ],
            "bodies": [
                "Hi,\n\nCould you please review the attached document and provide your feedback by EOD? The client is expecting our response tomorrow.\n\nThanks,\n{sender}",
                "Hello team,\n\nJust a reminder about our meeting tomorrow. Please come prepared with your weekly updates.\n\nBest,\n{sender}",
                "Hi,\n\nI've completed the initial draft of the technical specification. When you have a moment, please take a look and let me know if any changes are needed.\n\nRegards,\n{sender}",
                "Team,\n\nAttached are the notes from today's standup. Action items are highlighted. Please review and update your tasks accordingly.\n\nThanks,\n{sender}",
                "Hello,\n\nI wanted to follow up on our conversation about the new feature. Can we schedule a call this week to discuss next steps?\n\nBest regards,\n{sender}",
            ],
            "priorities": [EmailPriority.HIGH, EmailPriority.NORMAL, EmailPriority.NORMAL, EmailPriority.LOW],
            "requires_response": [True, True, True, False, True],
        },
    ],
    EmailCategory.PERSONAL: [
        {
            "senders": [
                ("mom@gmail.com", "Mom"),
                ("dad@outlook.com", "Dad"),
                ("bestfriend@yahoo.com", "Alex"),
                ("college_buddy@hotmail.com", "Chris"),
                ("neighbor@gmail.com", "Dave"),
                ("sister@gmail.com", "Sarah"),
            ],
            "subjects": [
                "Dinner this weekend?",
                "Check out these photos!",
                "Happy Birthday!",
                "Long time no see",
                "Recipe you asked for",
                "Planning the trip",
                "Congratulations!",
                "Quick question",
            ],
            "bodies": [
                "Hey!\n\nAre you free this weekend? Would love to catch up over dinner. Let me know what works for you!\n\nLove,\n{sender}",
                "Hi!\n\nJust wanted to share some photos from the trip. Hope you enjoy them! Can't wait to see you soon.\n\nMiss you,\n{sender}",
                "Happy Birthday! Hope you have an amazing day filled with joy and celebration!\n\nLove,\n{sender}",
                "Hey there!\n\nIt's been a while since we caught up. How have you been? Let's grab coffee sometime soon.\n\nCheers,\n{sender}",
                "Here's that recipe you asked for. It's really easy to make - just follow the steps and you'll be fine!\n\nEnjoy,\n{sender}",
            ],
            "priorities": [EmailPriority.NORMAL, EmailPriority.LOW, EmailPriority.LOW, EmailPriority.NORMAL],
            "requires_response": [True, False, True, True, False],
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
                ("pills@discount-pharmacy.net", "Cheap Meds"),
                ("dating@hot-singles.xyz", "Local Singles"),
                ("invest@guaranteed-returns.biz", "Investment Opportunity"),
            ],
            "subjects": [
                "YOU WON $1,000,000!!!",
                "Urgent: Your inheritance awaits",
                "FREE iPhone 15 - Claim NOW!",
                "Make $10,000/day from home",
                "Bitcoin secret revealed",
                "URGENT: Account suspended",
                "Your package is waiting",
                "Congratulations! You've been selected",
                "Act now - Limited time offer",
                "Re: Your recent inquiry",
            ],
            "bodies": [
                "CONGRATULATIONS!\n\nYou have been selected as our lucky winner! To claim your prize of $1,000,000, simply reply with your bank details.\n\nAct now before it's too late!",
                "Dear Friend,\n\nI am Prince Abdullah from Nigeria. I have $50 million that I need help transferring. You will receive 30% for your assistance.\n\nPlease respond urgently.",
                "You have been selected to receive a FREE iPhone 15! Click the link below to claim your prize:\n\nhttp://totally-not-spam.xyz/claim\n\nThis offer expires in 24 hours!",
                "URGENT NOTICE:\n\nYour account has been compromised. Click here immediately to verify your identity and secure your account.\n\nFailure to act will result in permanent suspension.",
                "Discover the secret that billionaires don't want you to know! Make unlimited money with this one simple trick. No experience needed!\n\nClick here to start earning TODAY!",
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
                ("weekly@hackernews.com", "Hacker News Weekly"),
                ("digest@substack.com", "Your Substack Digest"),
            ],
            "subjects": [
                "This week in tech",
                "Your daily digest",
                "Top products this week",
                "Morning Briefing",
                "Weekly roundup",
                "What you missed this week",
                "Trending stories",
            ],
            "bodies": [
                "Here's what you missed this week in tech:\n\n1. AI breakthrough announced\n2. New startup raises $100M\n3. Tech layoffs continue\n\nRead more on our website.",
                "Good morning!\n\nHere are today's top stories curated just for you:\n\n[Article 1: The Future of AI]\n[Article 2: Market Update]\n[Article 3: Tech News]\n\nHappy reading!",
                "This week's top trending stories:\n\n- Product launches\n- Industry news\n- Featured interviews\n\nDon't miss out on what's happening!",
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
                ("support@notion.so", "Notion Support"),
                ("team@linear.app", "Linear Support"),
            ],
            "subjects": [
                "Your support ticket #12345",
                "Action required: Verify your account",
                "Your request has been received",
                "Important security update",
                "Your subscription is expiring",
                "Service maintenance notice",
                "Your feedback request",
            ],
            "bodies": [
                "Hello,\n\nThank you for contacting support. Your ticket #12345 has been received and will be reviewed within 24 hours.\n\nBest,\nSupport Team",
                "Hi,\n\nWe noticed a login from a new device. If this was you, no action is needed. If not, please secure your account immediately.\n\nSecurity Team",
                "Your subscription will expire in 7 days. To continue uninterrupted service, please update your payment method.\n\nThank you for being a valued customer.",
                "Important: We've released a critical security update. Please update your integration to the latest version as soon as possible.\n\nRegards,\nSecurity Team",
            ],
            "priorities": [EmailPriority.HIGH, EmailPriority.URGENT, EmailPriority.NORMAL, EmailPriority.HIGH],
            "requires_response": [False, True, True, False],
        },
    ],
    EmailCategory.BILLING: [
        {
            "senders": [
                ("billing@company.com", "Billing Department"),
                ("invoices@vendor.com", "Vendor Invoicing"),
                ("noreply@paypal.com", "PayPal"),
                ("receipts@stripe.com", "Stripe"),
                ("accounting@company.com", "Accounting"),
            ],
            "subjects": [
                "Invoice #INV-2024-001",
                "Payment received - Thank you",
                "Your receipt from purchase",
                "Payment failed - Action required",
                "Expense report approval needed",
                "Monthly billing statement",
            ],
            "bodies": [
                "Please find attached your invoice for this month's services.\n\nAmount due: $1,234.56\nDue date: {due_date}\n\nThank you for your business.",
                "We've received your payment of $500.00.\n\nTransaction ID: TXN-12345\nDate: {date}\n\nThank you for your prompt payment!",
                "URGENT: Your payment method has failed. Please update your billing information to avoid service interruption.\n\nClick here to update your payment method.",
                "Your expense report for $2,456.78 requires approval. Please review the attached summary and approve or reject within 3 business days.",
            ],
            "priorities": [EmailPriority.NORMAL, EmailPriority.LOW, EmailPriority.URGENT, EmailPriority.HIGH],
            "requires_response": [False, False, True, True],
        },
    ],
}

# Urgent email scenarios
URGENT_SCENARIOS = [
    {
        "sender": ("ceo@company.com", "CEO"),
        "subject": "URGENT: Board meeting in 1 hour",
        "body": "I need the quarterly report immediately. The board is waiting and this is critical.\n\nPlease send ASAP.",
        "category": EmailCategory.WORK,
        "priority": EmailPriority.URGENT,
        "requires_response": True,
    },
    {
        "sender": ("security@bank.com", "Bank Security"),
        "subject": "URGENT: Suspicious activity detected",
        "body": "We've detected unusual activity on your account. Please verify your recent transactions immediately by calling our security line.\n\nThis is time-sensitive.",
        "category": EmailCategory.SUPPORT,
        "priority": EmailPriority.URGENT,
        "requires_response": True,
    },
    {
        "sender": ("oncall@company.com", "On-Call Alert"),
        "subject": "CRITICAL: Production server down",
        "body": "Alert: Production server is unresponsive.\n\nService: API Gateway\nStatus: DOWN\nTime: {time}\nImpact: All users affected\n\nImmediate action required.",
        "category": EmailCategory.WORK,
        "priority": EmailPriority.URGENT,
        "requires_response": True,
    },
    {
        "sender": ("client@important-corp.com", "Important Client"),
        "subject": "URGENT: Contract deadline today",
        "body": "We need to finalize the contract by end of day. Can you please review and sign the attached document?\n\nThis cannot wait until tomorrow.",
        "category": EmailCategory.WORK,
        "priority": EmailPriority.URGENT,
        "requires_response": True,
    },
]


# =============================================================================
# EMAIL GENERATION FUNCTIONS
# =============================================================================

def generate_timestamp(hours_ago: int = 0) -> str:
    """Generate an ISO timestamp for a given number of hours ago."""
    dt = datetime.now() - timedelta(hours=hours_ago)
    return dt.isoformat()


def generate_email(
    category: EmailCategory,
    is_urgent: bool = False,
    hours_ago: int = 0,
) -> Email:
    """
    Generate a single realistic email with ground truth labels.
    
    Args:
        category: The category for this email
        is_urgent: Whether to generate an urgent email
        hours_ago: How many hours ago the email was received
        
    Returns:
        Email object with ground truth labels set
    """
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
    
    # Shuffle emails to mix them up
    random.shuffle(emails)
    
    return emails


def generate_task_emails(task_id: str, difficulty: str) -> List[Email]:
    """
    Generate emails for a specific task based on difficulty.
    
    Args:
        task_id: The task identifier
        difficulty: easy, medium, or hard
        
    Returns:
        List of emails configured for the task
    """
    if difficulty == "easy":
        # Easy: 5 emails, clear categories, no spam, no urgent
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
        # Medium: 10 emails, some spam (~20%), one urgent
        return generate_email_batch(
            num_emails=10,
            spam_ratio=0.2,
            urgent_ratio=0.1,
        )
    
    else:  # hard
        # Hard: 20 emails, more spam (~25%), multiple urgent, tricky cases
        return generate_email_batch(
            num_emails=20,
            spam_ratio=0.25,
            urgent_ratio=0.15,
        )
