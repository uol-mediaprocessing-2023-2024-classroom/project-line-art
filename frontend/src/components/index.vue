<picture-input
  ref="pictureInput"
  :width="500"
  :removable="true"
  removeButtonClass="ui red button"
  :height="500"
  accept="image/jpeg, image/png, image/gif"
  buttonClass="ui button primary"
  :customStrings="{
  upload: '<h1>Upload it!</h1>',
  drag: 'Drag and drop your image here'}">

</picture-input>