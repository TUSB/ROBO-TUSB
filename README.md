[![GitHubの問題](https://img.shields.io/github/issues/TUSB/ROBO-TUSB.svg)](https://github.com/TUSB/ROBO-TUSB/issues)
[![GitHubフォーク](https://img.shields.io/github/forks/TUSB/ROBO-TUSB.svg)](https://github.com/TUSB/ROBO-TUSB/network)
[![GitHub星](https://img.shields.io/github/stars/TUSB/ROBO-TUSB.svg)](https://github.com/TUSB/ROBO-TUSB/stargazers)
[![GitHubライセンス](https://img.shields.io/github/license/TUSB/ROBO-TUSB.svg)](https://github.com/TUSB/ROBO-TUSB)
[![Twitter](https://img.shields.io/twitter/url/https/github.com/TUSB/ROBO-TUSB.svg?style=social)](https://twitter.com/intent/tweet?text=Wow:&url=https%3A%2F%2Fgithub.com%2FTUSB%2FROBO-TUSB)

# ROBO-TUSB
TUSBちゃんの支援用（TUSBちゃんではできないことをやってくれる）
## 使用方法
コマンドエイリアス: `?`

`<arg1> `: 必須

`[arg1]` : オプション

| コマンド | 説明
|---------|-------------|
| `help` | 使えるコマンドの一覧を表示します |
| `vote` | アンケートを開始します。 |
|---------|-------------|


| 管理コマンド | 説明
|---------|-------------|
| `alias` | エイリアスを変更します。 |
|---------|-------------|

最大20項目まで作成できます。

Vote コマンド基本構文

`vote "タイトル" "質問1;質問2;" --オプション`
## Voteコマンド例
`vote --title "あなたは赤い部屋が好きですか?" --options "はい;いいえ; " --duration "15" --notify`

`vote -T 好きなパイ -O ラズベリーパイ;オレンジパイ;しょぼパイ -D 7 -N`

ショートコード例

`vote -O Android;iOS`

`vote option1; option2`

### オプション

`--title , -T : タイトル`

`--options , -O : 質問`

`--duration , -D : 締め切り時間（分） 最大120分まで`

`--notify , -N : 通知設定`

## 確認済みのバグ

実行すると無限にhelpして停止するまでスパムメッセージを送る。
