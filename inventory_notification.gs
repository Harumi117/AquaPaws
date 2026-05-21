// =====================================================
// ★ここだけカスタマイズしてください
// =====================================================

// Chatwork設定
const CHATWORK_TOKEN  = "あなたのトークンをここに入力";
const CHATWORK_ROOM_ID = "あなたのルームIDをここに入力";

// スキップしたい回答（「問題ない」系の文言をすべて入れる）
const SKIP_VALUES = [
  "問題なし",
  "問題ない",
  "異常なし",
  "在庫あり",
  "十分",
  "OK",
  "ok",
];

// =====================================================
// メイン処理（変更不要）
// =====================================================

function onFormSubmit(e) {
  const responses = e.namedValues;
  const timestamp = responses["タイムスタンプ"] ? responses["タイムスタンプ"][0] : "";
  const staff     = responses["担当者名"]       ? responses["担当者名"][0]       : "不明";

  const items = [];

  for (const key in responses) {
    if (key === "タイムスタンプ" || key === "担当者名") continue;

    const value = responses[key][0];

    // 空、またはスキップ対象の回答は無視
    if (!value || value.trim() === "") continue;
    if (SKIP_VALUES.includes(value.trim())) continue;

    items.push("・" + key + "：" + value);
  }

  if (items.length === 0) return; // 送るものがなければ何もしない

  sendToChatwork(staff, timestamp, items);
}

function sendToChatwork(staff, timestamp, items) {
  const body =
    "[info][title]⚠️ 備品チェック報告[/title]" +
    "担当者：" + staff + "\n" +
    "記録時刻：" + timestamp + "\n\n" +
    items.join("\n") +
    "[/info]";

  const res = UrlFetchApp.fetch(
    "https://api.chatwork.com/v2/rooms/" + CHATWORK_ROOM_ID + "/messages",
    {
      method: "post",
      headers: { "X-ChatWorkToken": CHATWORK_TOKEN },
      payload: { body: body },
      muteHttpExceptions: true,
    }
  );

  // 送信結果をログに記録（エラー確認用）
  Logger.log("ステータス: " + res.getResponseCode());
  Logger.log("レスポンス: " + res.getContentText());
}
