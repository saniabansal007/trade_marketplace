from app import create_app, db
from app.models import User, Item

app = create_app()

with app.app_context():
    # Clear existing data
    print("Clearing old data...")
    db.drop_all()
    db.create_all()
    
    # Create test users
    print("Creating users...")
    user1 = User(username='Achilles', email='achilles@olympus.com')
    user1.set_password('password123')
    
    user2 = User(username='Odysseus', email='odysseus@olympus.com')
    user2.set_password('password123')
    
    db.session.add_all([user1, user2])
    db.session.commit()
    
    # Create test items
    print("Creating items...")
    items = [
        Item(
            name="Sword of Troy",
            description="A legendary blade forged in the fires of Mount Olympus, said to have slain countless foes in the Trojan War. Its edge never dulls.",
            category="weapon",
            rarity="legendary",
            seller_id=user1.id
        ),
        Item(
            name="Shield of Athena",
            description="Divine protection blessed by the goddess of wisdom herself. Provides unmatched defense in battle and reflects enemy attacks.",
            category="armor",
            rarity="epic",
            seller_id=user1.id
        ),
        Item(
            name="Potion of Strength",
            description="Grants temporary superhuman strength to the drinker. Brewed from rare herbs found only on Mount Olympus.",
            category="potion",
            rarity="rare",
            seller_id=user2.id
        ),
        Item(
            name="Bow of Artemis",
            description="A divine hunting bow that never misses its target. Blessed by the goddess of the hunt and the moon.",
            category="weapon",
            rarity="legendary",
            seller_id=user2.id
        ),
        Item(
            name="Scroll of Wisdom",
            description="Ancient knowledge written by the Oracle of Delphi. Contains prophecies and forgotten spells from the age of gods.",
            category="scroll",
            rarity="epic",
            seller_id=user1.id
        ),
        Item(
            name="Amulet of Zeus",
            description="A powerful artifact that channels the lightning of Zeus himself. Crackles with divine energy.",
            category="jewel",
            rarity="mythical",
            seller_id=user2.id
        ),
        Item(
            name="Helmet of Hades",
            description="The Helm of Darkness grants its wearer invisibility. Forged in the depths of the Underworld.",
            category="armor",
            rarity="mythical",
            seller_id=user1.id
        ),
        Item(
        name="Golden Fleece",
        description="The legendary Golden Fleece from Colchis. Said to have healing properties and bring prosperity to its owner.",
        category="artifact",
        rarity="legendary",
        seller_id=user2.id
            )
        ]

    db.session.add_all(items)
    db.session.commit()

    print(f"\n✅ Success!")
    print(f"   Created {User.query.count()} users")
    print(f"   Created {Item.query.count()} items")
    print(f"\n📝 Test Accounts:")
    print(f"   Username: Achilles  |  Password: password123")
    print(f"   Username: Odysseus  |  Password: password123")