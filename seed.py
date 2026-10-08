from app import create_app
from app.extensions import db
from app.models import User, Post, DirectMessage
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    # Drop all and recreate to apply schema changes
    db.drop_all()
    db.create_all()

    # Create Users
    u1 = User(
        username='alice', 
        email='alice@example.com', 
        password_hash=generate_password_hash('password123'), 
        bio='Hacking the planet.',
        profile_image='Alice_Profile.jpeg'
    )
    u2 = User(
        username='bob', 
        email='bob@example.com', 
        password_hash=generate_password_hash('password123'), 
        bio='Racing and coding.',
        profile_image='Bob_Profile.jpeg'
    )
    u3 = User(
        username='meme_machine', 
        email='meme@vip.com', 
        password_hash=generate_password_hash('password123'), 
        bio='Only top tier memes here.', 
        is_private=True,
        profile_image='meme_profile.jpg'
    )

    db.session.add_all([u1, u2, u3])
    db.session.commit()

    # Alice Posts
    p_a1 = Post(image_filename='Alice1.jpeg', caption='Best day at the park with my favorite buddy! 🐾🐶☀️', author=u1)
    p_a2 = Post(image_filename='Alice2.jpeg', caption='Late night coding session... powered by coffee and supervised by the cat! 💻☕️🐈', author=u1)
    p_a3 = Post(image_filename='Alice3.jpeg', caption='Cheers to good food and great company! 🍷✨', author=u1)

    # Bob Posts
    p_b1 = Post(image_filename='bob1.jpeg', caption='Track day! Adrenaline is pumping! 🏎️💨🏁', author=u2)
    p_b2 = Post(image_filename='bob2.jpeg', caption='Watching the match with the boys! Cheers! 🍻⚽️', author=u2)
    p_b3 = Post(image_filename='bob3.jpeg', caption='Morning stroll through the city before the busy day starts. ☕️🚶‍♂️🏙️', author=u2)

    # Meme Machine Posts
    p_m1 = Post(image_filename='meme1.png', caption='When the code works on the first try.', author=u3)
    p_m2 = Post(image_filename='meme2.webp', caption='Relatable 😂', author=u3)
    p_m3 = Post(image_filename='meme3.jpg', caption='Me IRL', author=u3)
    p_m4 = Post(image_filename='meme4.jpeg', caption='Every single day.', author=u3)
    p_m5 = Post(image_filename='meme5.webp', caption='Programming 101', author=u3)
    
    db.session.add_all([p_a1, p_a2, p_a3, p_b1, p_b2, p_b3, p_m1, p_m2, p_m3, p_m4, p_m5])
    db.session.commit()

    # Create some Direct Messages (IDOR target)
    dm1 = DirectMessage(sender_id=u3.id, receiver_id=u1.id, content='Hey Alice, here is the secret flag: FLAG{1D0R_15_4W3S0M3}')
    dm2 = DirectMessage(sender_id=u1.id, receiver_id=u3.id, content='Thanks! I will keep it safe.')
    dm3 = DirectMessage(sender_id=u2.id, receiver_id=u1.id, content='Hey Alice, did you get the flag from Meme Machine?')
    
    db.session.add_all([dm1, dm2, dm3])
    db.session.commit()

    print("Database seeded successfully with users, posts, and DMs!")
