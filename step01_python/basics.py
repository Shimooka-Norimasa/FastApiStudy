# 第1章: FastAPI を読むために必要な Python の基本
# 実行方法（C:FastApiStudystep01_python で）:  python basics.py

# ---------------------------------------------
# 1. 変数と型
# ---------------------------------------------
name = "太郎"        # 文字列 (str)
age = 20             # 整数 (int)
height = 170.5       # 小数 (float)
is_student = True    # 真偽値 (bool)  True / False

# f文字列: 文字列の前に f を付けると {} の中に変数を埋め込める
print(f"名前: {name}, 年齢: {age}, 身長: {height}, 学生: {is_student}")


# ---------------------------------------------
# 2. リスト (list) と 辞書 (dict)
# ---------------------------------------------
fruits = ["りんご", "みかん", "ぶどう"]   # リスト: 順番のあるデータの並び
fruits.append("もも")                     # 末尾に追加
print(fruits[0])                          # 0番目(先頭)を取り出す -> りんご

user = {"name": "花子", "age": 25}        # 辞書: 「キー: 値」の組
print(user["name"])                       # キーで値を取り出す -> 花子
user["email"] = "hanako@example.com"      # 新しいキーを追加


# ---------------------------------------------
# 3. if 文 と for 文（インデント=字下げ がブロックを表す）
# ---------------------------------------------
if age >= 20:
    print("成人です")
else:
    print("未成年です")

for fruit in fruits:
    print(f"- {fruit}")

for i, fruit in enumerate(fruits):   # enumerate で番号も一緒に取れる
    print(i, fruit)


# ---------------------------------------------
# 4. 関数 と 型ヒント
# ---------------------------------------------
# def 関数名(引数: 型) -> 戻り値の型:
# 「: str」や「-> str」は型ヒント。Python自体は無視するが、
# FastAPI はこれを読み取って入力チェックに使う（重要！）
def greet(name: str, polite: bool = False) -> str:
    if polite:
        return f"{name}様、こんにちは"
    return f"{name}さん、こんにちは"


print(greet("太郎"))                 # polite は省略 -> デフォルト値 False
print(greet("花子", polite=True))    # キーワード引数で指定


# ---------------------------------------------
# 5. デコレータ（@ で始まる行）
# ---------------------------------------------
# デコレータは「関数に追加の働きを付け加える仕組み」。
# FastAPI の @app.get("/") は「この関数を / へのアクセス時に呼んでね」と登録している。
# ここでは仕組みを理解するために、自作の簡単なデコレータを作ってみる。
routes = {}   # URL と 関数 の対応表


def route(path: str):
    def register(func):
        routes[path] = func   # 対応表に登録するだけ
        return func
    return register


@route("/hello")
def hello():
    return "Hello!"


@route("/bye")
def bye():
    return "Bye!"


# 対応表から URL に合う関数を取り出して呼ぶ（Webフレームワークがやっていることの超簡易版）
for path in ["/hello", "/bye"]:
    print(path, "->", routes[path]())


# ---------------------------------------------
# 6. with 文
# ---------------------------------------------
# with は「使い終わったら自動で後片付け(close)してくれる」書き方。
# ファイルやデータベース接続でよく使う。
with open("sample.txt", "w", encoding="utf-8") as f:
    f.write("with を抜けると自動でファイルが閉じられます\n")

with open("sample.txt", encoding="utf-8") as f:
    print(f.read())
