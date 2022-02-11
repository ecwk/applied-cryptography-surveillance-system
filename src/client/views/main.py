from util.config import config

def main(**props):
  cameraOn = props['cameraOn']
  cameraOnStr = {
    'text': [f'Camera On: ', str(cameraOn)],
  }

  if cameraOn:
    cameraOnStr['color'] = [None, [(0, 255, 0), None]]
  else:
    cameraOnStr['color'] = [None, [(255, 0, 0), None]]


  return {
    'title': [
      {
       'text': [f'{config["DEFAULT"]["username"]}' , ' ⬤'],
       'types': [['bold'], None],
       'color': [None, [cameraOnStr['color'][1][0], None]],
      }
    ],
    'bodyHeader': [{ 'text': ['Status'] }],
    'body': [
      cameraOnStr
    ]
  }

mainViews = {
  'main': main
}