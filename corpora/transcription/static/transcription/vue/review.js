
<script	type="text/javascript">

var template = `

	


`



Vue.component('v-test', {
  delimiters: ['${', '}']
	props: ['message'],
	template: `
		<div>{{message}}</div>
	`,
})

new Vue({
  delimiters: ['${', '}']
  el: '#vue-app',
})

</script>