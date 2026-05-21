/**
 * Googleフォーム送信時に実行される関数
 *
 * 【重要】このコードはシンプルトリガーではなく「インストーラブルトリガー」として登録してください。
 * 設定方法: スクリプトエディタ → 左メニュー「トリガー」→「トリガーを追加」
 *   - 実行する関数: onFormSubmit
 *   - イベントのソース: フォームから
 *   - イベントの種類: フォーム送信時
 *
 * 【事前設定】スクリプトのプロパティにAPIトークンを保存してください:
 *   スクリプトエディタ → 「プロジェクトの設定」→「スクリプト プロパティ」
 *   CHATWORK_TOKEN = あなたのトークン
 *   CHATWORK_ROOM_ID = あなたのルームID
 */

function onFormSubmit(e) {
  try {
    const responses = e.namedValues;
    const timestamp = responses["タイムスタンプ"] ? responses["タイムスタンプ"][0] : new Date().toString();
    const staff = responses["担当者名"] ? responses["担当者名"][0] : "不明";

    const ss = SpreadsheetApp.openById("11a1vFnQybUPuCRqBPy8mjL_N693NNbblyN6o5myaSSEQ");
    const targetSheet = ss.getSheetByName("発注候補一覧");

    if (!targetSheet) {
      Logger.log("シート「発注候補一覧」が見つかりません。シート名を確認してください。");
      return;
    }

    let orderItems = [];   // 「発注が必要」な備品
    let remarksItems = []; // 備考欄に記載があるもの

    for (let key in responses) {
      if (key === "タイムスタンプ" || key === "担当者名") continue;

      const value = responses[key][0];
      if (!value || value.trim() === "") continue;

      // 「発注が必要」「不足」「少ない」を含む回答を発注リストへ
      const needsOrder = value.includes("発注") || value.includes("不足") || value.includes("少ない") || value.includes("切れ");

      // 「備考」を含む質問名の回答は備考リストへ
      const isRemark = key.includes("備考") || key.includes("メモ") || key.includes("コメント");

      targetSheet.appendRow([timestamp, staff, key, value]);

      if (isRemark && value.trim() !== "") {
        remarksItems.push("【備考】" + key + " : " + value);
      } else if (needsOrder) {
        orderItems.push("・" + key + " → " + value);
      } else {
        orderItems.push("・" + key + " : " + value);
      }
    }

    if (orderItems.length > 0 || remarksItems.length > 0) {
      sendToChatwork(staff, timestamp, orderItems, remarksItems);
    }

  } catch (error) {
    Logger.log("エラーが発生しました: " + error.toString());
    // エラー時はメールで通知（スクリプトを実行しているGoogleアカウントに送られます）
    MailApp.sendEmail(
      Session.getActiveUser().getEmail(),
      "【AquaPaws】備品チェックスクリプトエラー",
      "エラー内容:\n" + error.toString()
    );
  }
}

function sendToChatwork(staff, timestamp, orderItems, remarksItems) {
  // スクリプトプロパティからトークンを取得（直接書かずに管理）
  const props = PropertiesService.getScriptProperties();
  const token = props.getProperty("CHATWORK_TOKEN");
  const roomId = props.getProperty("CHATWORK_ROOM_ID");

  if (!token || !roomId) {
    Logger.log("Chatworkのトークンまたはルームが設定されていません。スクリプトプロパティを確認してください。");
    return;
  }

  let bodyLines = [];
  bodyLines.push("担当者: " + staff);
  bodyLines.push("記録時刻: " + timestamp);
  bodyLines.push("");

  if (orderItems.length > 0) {
    bodyLines.push("▼ 発注・在庫状況");
    bodyLines = bodyLines.concat(orderItems);
  }

  if (remarksItems.length > 0) {
    bodyLines.push("");
    bodyLines.push("▼ 備考");
    bodyLines = bodyLines.concat(remarksItems);
  }

  const body = "[info][title]備品チェック報告[/title]" + bodyLines.join("\n") + "[/info]";

  const response = UrlFetchApp.fetch("https://api.chatwork.com/v2/rooms/" + roomId + "/messages", {
    "method": "post",
    "headers": { "X-ChatWorkToken": token },
    "payload": { "body": body },
    "muteHttpExceptions": true
  });

  const statusCode = response.getResponseCode();
  if (statusCode !== 200) {
    Logger.log("Chatwork送信失敗。ステータスコード: " + statusCode + " レスポンス: " + response.getContentText());
  }
}

/**
 * スクリプトプロパティにChatworkの認証情報を保存するセットアップ関数
 * 一度だけ手動実行してください
 */
function setupProperties() {
  const props = PropertiesService.getScriptProperties();
  props.setProperty("CHATWORK_TOKEN", "ここにChatworkトークンを入力");
  props.setProperty("CHATWORK_ROOM_ID", "ここにルームIDを入力");
  Logger.log("プロパティを設定しました。");
}
