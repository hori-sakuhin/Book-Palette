from flask import Flask, render_template, request, redirect, url_for,session
from werkzeug.utils import secure_filename
import os
import mysql.connector

app = Flask(__name__)
# セッションの暗号化に使用する秘密鍵を設定
# 今ログインしているのは誰かを識別するために使用する
app.secret_key = "book_app_secret_key"


def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="your database account",
        password="your database password",
        database="book_app"
    )


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor()

        sql = """
            INSERT INTO users (username, email, password)
            VALUES (%s, %s, %s)
        """

        cursor.execute(sql, (username, email, password))

        conn.commit()

        cursor.close()
        conn.close()

        return redirect(url_for("login"))

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        sql = """
            SELECT user_id, username, password
            FROM users
            WHERE email = %s
        """

        cursor.execute(sql, (email,))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user and user["password"] == password:

            session["user_id"] = user["user_id"]
            session["username"] = user["username"]

            return redirect(url_for("top"))

        return "メールアドレスまたはパスワードが違います"



    return render_template("login.html")



# ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー
# ホーム画面

@app.route("/top")
def top():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
        SELECT book_id, title, author, genre, book_type,
               cover_image, summary, recommendation
        FROM books
        ORDER BY book_id DESC
        LIMIT 6
    """

    cursor.execute(sql)

    books = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("top.html", books=books)

# ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー
# 図書検索

@app.route("/search")
def search():

    keyword = request.args.get("keyword", "")
    books = []

    if keyword:

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        sql = """
            SELECT book_id, title, author, genre, book_type,
                   summary, recommendation
            FROM books
            WHERE title LIKE %s
               OR author LIKE %s
               OR genre LIKE %s
               OR book_type LIKE %s
            ORDER BY book_id DESC
        """

        search_word = "%" + keyword + "%"

        cursor.execute(sql, (
            search_word,
            search_word,
            search_word,
            search_word
        ))

        books = cursor.fetchall()

        cursor.close()
        conn.close()

    return render_template(
        "search.html",
        books=books,
        keyword=keyword
    )


# ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー
# 本の詳細

@app.route("/book/<int:book_id>")
def book_detail(book_id):

    keyword = request.args.get("keyword", "")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
        SELECT book_id, title, author, genre, book_type,
            cover_image, summary, recommendation
        FROM books
        WHERE book_id = %s
    """

    cursor.execute(sql, (book_id,))
    book = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template(
        "book_detail.html",
        book=book,
        keyword=keyword
    )


# ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー
# おすすめ本の登録

@app.route("/register_book", methods=["GET", "POST"])
def register_book():

    if request.method == "POST":

        title = request.form["title"]
        author = request.form["author"]
        genre = request.form["genre"]
        book_type = request.form["book_type"]
        summary = request.form["summary"]
        recommendation = request.form["recommendation"]

        user_id = session["user_id"]

        # 表紙画像を取得
        file = request.files.get("cover_image")

        cover_image = None

        if file and file.filename:
            filename = secure_filename(file.filename)

            upload_folder = os.path.join(
                app.static_folder,
                "uploads"
            )

            os.makedirs(upload_folder, exist_ok=True)

            file.save(
                os.path.join(upload_folder, filename)
            )

            cover_image = "uploads/" + filename

        conn = get_db_connection()
        cursor = conn.cursor()

        sql = """
            INSERT INTO books
            (user_id, title, author, genre, book_type,
             cover_image, summary, recommendation)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """

        cursor.execute(sql, (
            user_id,
            title,
            author,
            genre,
            book_type,
            cover_image,
            summary,
            recommendation
        ))

        conn.commit()

        cursor.close()
        conn.close()

        return redirect(url_for("register_book"))

    return render_template("Register_book.html")

# ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー
# 登録内容編集


@app.route("/edit_book/<int:book_id>", methods=["GET", "POST"])
def edit_book(book_id):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":

        title = request.form["title"]
        author = request.form["author"]
        genre = request.form["genre"]
        book_type = request.form["book_type"]
        summary = request.form["summary"]
        recommendation = request.form["recommendation"]

        file = request.files.get("cover_image")

        if file and file.filename:
            filename = secure_filename(file.filename)

            upload_folder = os.path.join(
                app.static_folder,
                "uploads"
            )

            os.makedirs(upload_folder, exist_ok=True)

            file.save(
                os.path.join(upload_folder, filename)
            )

            cover_image = "uploads/" + filename

            sql = """
                UPDATE books
                SET title=%s,
                    author=%s,
                    genre=%s,
                    book_type=%s,
                    cover_image=%s,
                    summary=%s,
                    recommendation=%s
                WHERE book_id=%s
                  AND user_id=%s
            """

            cursor.execute(sql, (
                title,
                author,
                genre,
                book_type,
                cover_image,
                summary,
                recommendation,
                book_id,
                session["user_id"]
            ))

        else:

            sql = """
                UPDATE books
                SET title=%s,
                    author=%s,
                    genre=%s,
                    book_type=%s,
                    summary=%s,
                    recommendation=%s
                WHERE book_id=%s
                  AND user_id=%s
            """

            cursor.execute(sql, (
                title,
                author,
                genre,
                book_type,
                summary,
                recommendation,
                book_id,
                session["user_id"]
            ))

        conn.commit()

        cursor.close()
        conn.close()

        return redirect(url_for("recommend"))

    cursor.execute("""
        SELECT *
        FROM books
        WHERE book_id=%s
          AND user_id=%s
    """, (book_id, session["user_id"]))

    book = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template("edit_book.html", book=book)


# ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー
# 登録本削除

@app.route("/delete_book/<int:book_id>", methods=["POST"])
def delete_book(book_id):

    conn = get_db_connection()
    cursor = conn.cursor()

    sql = """
        DELETE FROM books
        WHERE book_id=%s
          AND user_id=%s
    """

    cursor.execute(sql, (
        book_id,
        session["user_id"]
    ))

    conn.commit()

    cursor.close()
    conn.close()

    return redirect(url_for("recommend"))


# ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー
# 他のユーザーがおすすめした本

@app.route("/other_recommend")
def other_recommend():

    user_id = session["user_id"]

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
        SELECT book_id, title, author, genre, book_type,
               summary, recommendation
        FROM books
        WHERE user_id != %s
        ORDER BY book_id DESC
    """

    cursor.execute(sql, (user_id,))
    books = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("other_recommend.html", books=books)



# ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー
# マイページ

@app.route("/mypage")
def mypage():



    user_id = session["user_id"]

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
        SELECT username, email
        FROM users
        WHERE user_id = %s
    """

    cursor.execute(sql, (user_id,))
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template(
        "mypage.html",
        username=user["username"],
        email=user["email"]
    )


# ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー
# ログアウト

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))



# ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー
# おすすめした本一覧

@app.route("/recommend")
def recommend():

    user_id = session["user_id"]

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
        SELECT book_id, title, author, genre, book_type,
               summary, recommendation
        FROM books
        WHERE user_id = %s
        ORDER BY book_id DESC
    """

    cursor.execute(sql, (user_id,))
    books = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("recommend.html", books=books)




if __name__ == "__main__":
    app.run(debug=True)