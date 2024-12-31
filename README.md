# S.T.D.N.iRMap

## What is this?-これは何?

S.T.D.N.iRMap is a open source track map overlay for iRacing.  
S.T.D.N.iRMapはiRacingのためのオープンソーストラックマップオーバーレイです。

![S.T.D.N.iRMap](./assets/images/readme.png)

## Installation-インストール

- Download the latest release from the [Releases](https://github.com/ellettie/S.T.D.N.iRMap/releases) page.  
[Releases](https://github.com/ellettie/S.T.D.N.iRMap/releases)ページから最新のリリースをダウンロードしてください。

## Features-機能

- This application generates a map from the user's telemetry data.  
このアプリケーションは、ユーザのテレメトリーデータからマップを生成します。 
   
- To generate a map, you need to drive without recording incidents.  
マップを生成するために、インシデントを記録せずに走行する必要があります。

- The map is generated at the half point of the track. You need to drive at least 1.5 laps.  
マップの生成はコースの半分地点で行います。最短で1.5周走行する必要があります。   

- The track data is saved as `tracks\track_name.pkl`.  
コースのデータは`tracks\track_name.pkl`として保存されます。

## Usage-使用方法

⚠️ For operation in a Python environment, `python run.py`    
Python環境で実行する場合は`python run.py`を実行してください。

1. Run iRacing with borderless window mode.  
   iRacingはボーダーレスウィンドウモードで実行してください。  

2. Drive until the track is displayed.  
   トラックが表示されるまで走行します。

3. Press the "Set Unupdatable" button in the UI to stop updating the map.  
   UIの"更新不可にする"ボタンを押すことで、コースの更新を停止できます。

4. Press the "Delete Track" button in the UI to delete the track and the file.  
   UIの"トラックを削除"ボタンを押すことで、トラックとファイルを削除できます。

## Requirements-要件

⚠️ For operation in a Python environment  
Python環境での動作の場合

- Python 3.11
- PySide6 6.8.0  
   `pip install PySide6==6.8.0`

- NumPy 1.24.0  
   `pip install numpy==1.24.0`

- pyirsdk 1.3.5  
   `pip install pyirsdk==1.3.5`

## License-ライセンス

S.T.D.N.iRMap is licensed under the MIT License.  
However, this project uses third-party libraries, each with its own license terms, including:  
S.T.D.N.iRMapはMITライセンスでライセンスされています。  
ただし、このプロジェクトは以下を含むサードパーティライブラリを使用しています。各ライブラリにはそれぞれのライセンス条件があります:
- Python 3 (PSFL)
- PySide6 (LGPL)
- shiboken6 (LGPL)
- NumPy (BSD 3-Clause)
- pyirsdk (MIT)
- PyYAML (MIT)

For detailed license terms and notices of third-party software, please refer to the [THIRDPARTYNOTICES.txt](THIRDPARTYNOTICES.txt) .  
サードパーティソフトウェアの詳細なライセンス条件については、[THIRDPARTYNOTICES.txt](THIRDPARTYNOTICES.txt) を参照してください。



