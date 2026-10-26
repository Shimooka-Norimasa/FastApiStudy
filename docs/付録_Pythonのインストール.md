# 付録 Python のインストール

> Python がすでに入っている人は読み飛ばして構いません。
> 確認方法は [3. インストールできたか確認する](#3-インストールできたか確認する) を見てください。

## この付録のねらい

- 教材を始める前に、Python を正しくインストールする
- 初心者がつまずきやすい「`python` コマンドが見つからない」問題を避ける

## この付録が終わるとできること

- ターミナル（PowerShell など）で `python --version` を実行するとバージョンが表示される
- [第0章 準備](00_準備.md) に進める

---

## 1. Windows の場合

Windows では **Python install manager**（Python のインストールとバージョン管理を行う公式ツール）を使うのが、現在の公式の推奨です。

### 1-1. Python install manager を入れる

次のどちらか好きな方法で入れてください。中身は同じです。

**方法A: Microsoft Store から（いちばん簡単）**

1. スタートメニューから「Microsoft Store」を開く
2. 「Python install manager」で検索する
3. 「入手」（または「インストール」）を押す

**方法B: python.org から**

1. https://www.python.org/downloads/ を開く
2. Windows 向けの「Python install manager」をダウンロードする
3. ダウンロードしたファイルをダブルクリックしてインストールする

### 1-2. Python 本体を入れる

PowerShell を開いて（スタートメニューで「PowerShell」と検索）、次を実行します。

```powershell
python
```

初回は、最新の Python をインストールするかどうか確認されることがあります。画面の指示に従って進めてください（`y` を入力して Enter など）。

インストールが終わると、次のような表示になります。

```
Python 3.x.x (...) on win32
Type "help", "copyright", "credits" or "license" for more information.
>>>
```

`>>>` は Python の対話モードです。`exit()` と入力すると終了します。

### 1-3. 古いインストーラー（.exe）を使う場合

インターネットの解説記事では、`python-3.x.x-amd64.exe` のようなインストーラーがよく紹介されています。
この方式は Python 3.14 から **非推奨** になり、3.16 以降では提供されなくなる予定です。

それでも使う場合は、最初の画面で **「Add python.exe to PATH」に必ずチェックを入れてから**「Install Now」を押してください。
このチェックを忘れると `python` コマンドが使えません（初心者がいちばんつまずく点です）。

```
┌──────────────────────────────────────────┐
│ Install Python 3.x.x                     │
│                                          │
│  → Install Now                           │
│  → Customize installation                │
│                                          │
│  ☐ Use admin privileges when installing  │
│  ☑ Add python.exe to PATH   ← ここ！      │
└──────────────────────────────────────────┘
```

---

## 2. Mac の場合

1. https://www.python.org/downloads/ を開き、macOS 向けのインストーラー（`.pkg`）をダウンロードする
2. ダウンロードしたファイルを開き、画面の指示に従ってインストールする
3. インストール後に開く Finder のウィンドウにある「**Install Certificates.command**」をダブルクリックする
   （これを実行しないと、`pip install` が証明書エラーで失敗することがあります）

> **Mac でのコマンド名の注意**
> Mac では `python` ではなく **`python3`** と入力します。
> ```bash
> python3 --version
> python3 -m venv .venv
> ```
> 仮想環境を有効化した後（第0章）は、`python` と `pip` で動きます。

---

## 3. インストールできたか確認する

ターミナルを **新しく開き直して** から実行します（インストール前に開いていたターミナルには設定が反映されていないため）。

```powershell
python --version      # Mac は python3 --version
```

```
Python 3.x.x
```

のようにバージョンが表示されれば成功です。[第0章 準備](00_準備.md) に進んでください。

---

## 4. うまくいかないとき

### `python` と入力すると Microsoft Store が開く／「見つかりません」と表示される（Windows）

Windows に最初から入っている「アプリ実行エイリアス」の設定が原因のことがあります。

1. スタートメニューで「**アプリ実行エイリアスの管理**」を検索して開く
2. 「Python」や「Python install manager」に関係する項目がオンになっているか確認する
3. すでにオンなら、一度オフにしてからもう一度オンにする
4. PowerShell を開き直して `python --version` を試す

古いインストーラー（1-3）で入れた場合は、「Add python.exe to PATH」のチェック忘れが考えられます。
インストーラーをもう一度実行し、チェックを入れて入れ直すのが確実です。

### `pip install` が失敗する（最新の Python の場合）

出たばかりの Python のバージョンでは、ライブラリの対応が追いついていないことがあります。
その場合は、一つ前のバージョン（例: 3.13）を入れて、そのバージョンで仮想環境を作ってください（Windows）。

```powershell
py install 3.13
py -V:3.13 -m venv .venv
```

この教材は Python 3.12 で動作確認しています。**3.10 以上** を使ってください。

### 会社のネットワークで `pip install` ができない

社内ネットワークでは、プロキシの設定が必要な場合があります。社内の情報システム担当者に確認してください。

---

## 参考

- Python 公式: Windows で Python を使う https://docs.python.org/ja/3/using/windows.html
- Python 公式: Mac で Python を使う https://docs.python.org/ja/3/using/mac.html
