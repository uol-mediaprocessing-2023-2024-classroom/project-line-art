import Vue from 'vue'
import App from './App.vue'
import vuetify from './plugins/vuetify'
import SvgIcon from '@jamescoyle/vue-icon';
import { mdiReload } from '@mdi/js';
import FormDataPost from './upload';

Vue.config.productionTip = false

new Vue({
  vuetify,
  render: h => h(App)
}).$mount('#app')

FormDataPost('http://localhost:8000/user/picture', image)
  .then(response=>{
    console.log("Uploaded picture successfully");
  })
  .catch(err=>{
    console.error(err);
  });
