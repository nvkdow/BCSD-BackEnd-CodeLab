'''
 필요한 라이브러리를 불러오는 코드입니다.
 C/C++ 프로그램의 #include <header_file> 과 동일하다고 생각하시면 됩니다.
'''
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

'''
 전역 변수를 설정해주는 코드입니다.
 아래 app.config['...']는 데이터베이스를 위한 설정이며
 db = SQLAlchemy(...) 코드로 데이터베이스 객체를 생성합니다.
'''
app = Flask(__name__)
app.config['SECRET_KEY'] = 'seecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///codelab.db'
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False

db = SQLAlchemy(app)

# 데이터베이스에 데이터를 삽입하거나 가져올 때 이용할 클래스입니다.
class Article(db.Model):
    __table_name__ = 'article'
    # 데이터베이스 테이블을 구성하는 열(column)들을 선언해줍니다.
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    author = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.TEXT)
    created_at = db.Column(db.DateTime, default=datetime.now())

    def __init__(self, author, title, content):
        self.author, self.title, self.content = author, title, content

db.create_all()


'''
 [ CONTROLLER ]
 URL 형식(예시 http://localhost:5000/index)으로 들어오는 요청에 대해 알맞은 반환값을 돌려주는 Controller 영역입니다.
 index 함수는 url이 '/', '/index' 로 끝나는 요청에 대해 호출되고
 article 함수는 url이 '/article'로 끝나는 요청에 대해 호출됩니다.
 article_for 함수는 url이 '/article/<id>' 로 끝나는 요청에 대해 호출됩니다.
 <id>부분은 어떤 글자든 받아서 id 변수에 저장하겠단 뜻입니다. 변수명에서 알 수 있듯, 게시글의 번호가 넘어가게 됩니다.
 예시로 14번 게시글에 접근하면 http://url/article/14 형식으로 요청을 생성하게 될 것입니다.
'''
@app.route('/')
@app.route('/index')
def index():
    '''
     index는 홈페이지의 첫 화면입니다.
     현재 작성된 글의 리스트가 표현되어야 하므로 데이터베이스에 연결해서 해당 정보를 반환하는
     getArticleList() 함수를 호출합니다.
    '''
    articles = getArticleList()
    return render_template('index.html', articles=articles)

@app.route('/article', methods=['POST', 'GET'])
def article():
    '''
     article 함수는 글 작성 페이지에 의해 호출됩니다.
     이 함수에서 작성된 글의 정보(작성자, 제목, 내용)을 DB에 저장하는 함수인
     postArticle(...)을 호출하게 됩니다.
    '''
    if request.method == 'POST': # 요청의 방법이 'POST' 일 때,
        if postArticle(request.form): # postArticle 함수로 글의 정보를 DB에 추가하는 것이 성공한다면
            return redirect('index') # 다시 초기화면으로 이동시킵니다.

    return render_template('post_article.html') # 그 외엔 글 작성 페이지로 이동합니다.

@app.route('/article/<id>')
def article_for(id):
    '''
     article_for 함수는 특정 게시물의 내용을 화면에 표시하기 위한 함수입니다.
     특정 게시글의 모든 정보가 필요하므로 getArticle(...) 함수를 호출합니다.
    '''
    article = getArticle(id)
    return render_template('article.html', article=article)


'''
 [ MODEL ]
 CONTROLLER에게 호출되어 필요한 정보를 DB로 부터 반환하는 MODEL 영역입니다.
 여기있는 함수들이 실제 DB와 상호작용하며 필요하다면 임의의 작업을 수행해줍니다.
'''
def getArticleList():
    '''
     getArticleList 함수는 데이터베이스에 접근하여
     게시글 정보의 리스트를 가져옵니다.
     그리고 적절한 가공 후에 이러한 데이터를 반환하게 됩니다.
    '''
    ret = []
    results = Article.query.all() # 데이터베이스에서 Article(게시글) 정보의 리스트를 가져오는 코드입니다.
    for result in results: # 가져온 게시글 정보의 리스트에서 각 정보마다
        ret.append(result.__dict__) # 'key':'value' 형식으로 변경하여 ret 리스트에 추가합니다.

    # 가공된 리스트는 [{'id':1, 'author':'이름', 'title':'제목', 'content':'내용', 'created_at':작성일}, ... ] 형식을 띄게 됩니다.
    return ret

def getArticle(id):
    '''
     getArticle 함수는 데이터베이스에 접근하여
     특정 게시글의 정보를 가져옵니다.
     이 함수 역시 getArticleList와 동일한 가공을 수행합니다.
    '''
    # 데이터베이스에서 Article(게시글) 중 id가 함수의 인자로 넘어온 id와 동일한 게시글의 정보를 가져옵니다.
    # 그런 게시글이 없다면은 404 오류를 띄웁니다.
    ret = Article.query.filter_by(id=id).first_or_404(description='There is no such id as {}'.format(id))

    # 가져온 데이터 ret도 getArticleList()의 데이터 처럼 'key':'value' 형식으로 반환합니다.
    # 반환값은 {'id':1, 'author':'이름', 'title':'제목', 'content':'내용', 'created_at':작성일} 형식을 띄게 됩니다.
    return ret.__dict__

def postArticle(data):
    '''
     postArticle 함수는 사용자가 입력한 게시글 정보를 데이터베이스에 저장합니다.
     작성자, 제목, 내용 데이터를 입력받으면 이를 데이터베이스에 삽입합니다. 작성일자는 자동으로 생성됩니다.
    '''
    # if not data['author'].strip() or not data['title'].strip():
    #     return False
    # 전달받은 사용자의 입력값 author, title, content로 Article 객체를 생성합니다.
    article = Article(author=data['author'], title=data['title'], content=data['content'])
    # 생성한 객체를 데이터베이스에 삽입합니다.
    db.session.add(article)
    db.session.commit()
    return True


# 기존 C/C++ 프로그램의 Main 함수에 해당하는 부분입니다.
# 지금은 단순히 프로그램 실행을 위한 함수만을 호출합니다.
if __name__ == '__main__':
    app.run()
