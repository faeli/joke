from joke.fair.db_url import connect as db_url_connect
from joke.fair.model import Model
from joke.fair import fairdb

class TestModel(Model):
    TEST_SQL = '''SELECT 1+1 ;'''
    
    @fairdb
    def test(self):
        pass
        
    class Meta:
        database = db_url_connect('sqlite:///test.db')
    
    

def test_model():
    model = TestModel(name="asdfa")
    assert model.test().fetchone()[0] == 2