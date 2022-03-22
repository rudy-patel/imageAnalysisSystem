from main import Users

def test_new_user():
    name = "Test"
    email = 'test@gmail.com'

    user = Users(name=name, email=email)
    
    assert user.name == name
    assert user.email == email
