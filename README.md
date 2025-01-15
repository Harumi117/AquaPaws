# 犬の1日必要水分量計算アプリ 🐾

このアプリは、犬の体重に基づいて1日に必要な水分量を計算するシンプルなツールです。愛犬の健康管理に役立ててください！🌟

## 機能

- **水分量の計算**  
  わんちゃんの体重を入力することで、1日に必要な水分量を簡単に計算できます。
  
- **計算結果の表示**  
  体重に基づいて計算された水分量（ml）が表示されます。

- **補足情報の提供**  
  季節や運動量に応じた調整の必要性をアドバイスします。

---

## 使用方法

1. **インストール**  
   Python 3.9以上が必要です。以下のコマンドを使用して必要なライブラリをインストールしてください。  

   ```bash
   pip install streamlit
   ```

2. **アプリの実行**  
   ターミナルで以下のコマンドを入力してアプリを起動します。  

   ```bash
   streamlit run app.py
   ```

3. **入力と結果の確認**  
   - アプリが起動したら、体重を入力し、「水分量を計算する」ボタンをクリックします。
   - 計算結果が表示されます。

---

## 計算式

このアプリでは、Resting Energy Requirement (RER) を基に以下の計算を行っています：

\[
RER = 70 \times (体重^{0.75})
\]

水分量はRERと同じ値を目安としています。

---

## 注意事項

- 本アプリの計算結果は目安であり、すべての犬に当てはまるわけではありません。
- わんちゃんの個別の状況（年齢、活動量、季節など）に応じて調整してください。
- 詳細なアドバイスについては、獣医師に相談してください。

---

## 貢献

フィードバックや提案は歓迎します！以下の手順でプロジェクトに貢献できます：

1. このリポジトリをフォークします。
2. ブランチを作成します：`git checkout -b feature/新機能`
3. 変更をコミットします：`git commit -m 'Add some 新機能'`
4. プッシュします：`git push origin feature/新機能`
5. プルリクエストを作成します。

---

## ライセンス

このプロジェクトはMITライセンスの下で提供されています。詳細については、[LICENSE](LICENSE)ファイルをご確認ください。
