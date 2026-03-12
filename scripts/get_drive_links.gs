// Sora Distribution Pipeline — Google Apps Script
// Crawls a Google Drive folder (and all subfolders), makes every .mp4 publicly viewable,
// and outputs a two-column spreadsheet: filename | drive_url
//
// HOW TO USE:
// 1. Go to script.google.com and create a new project
// 2. Paste this entire script
// 3. Replace PASTE_YOUR_FOLDER_ID_HERE with the ID from your Drive folder URL
//    (the long string after /folders/ in the URL)
// 4. Click Run → getVideoLinks
// 5. A new Google Sheet called "SoraGirls_DriveLinks" will appear in your Drive
// 6. Download it: File → Download → Comma-separated values (.csv)

function getVideoLinks() {
  var folderId = 'PASTE_YOUR_FOLDER_ID_HERE';
  var ss = SpreadsheetApp.create('SoraGirls_DriveLinks');
  var sheet = ss.getActiveSheet();
  sheet.appendRow(['filename', 'drive_url']);
  processFolder(DriveApp.getFolderById(folderId), sheet);
  Logger.log('Done! Spreadsheet URL: ' + ss.getUrl());
}

function processFolder(folder, sheet) {
  var files = folder.getFiles();
  while (files.hasNext()) {
    var file = files.next();
    if (file.getName().endsWith('.mp4')) {
      file.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW);
      var id = file.getId();
      sheet.appendRow([
        file.getName(),
        'https://drive.google.com/file/d/' + id + '/view?usp=sharing'
      ]);
    }
  }
  var subs = folder.getFolders();
  while (subs.hasNext()) processFolder(subs.next(), sheet);
}
