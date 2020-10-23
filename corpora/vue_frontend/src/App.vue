<template>
  <div id="nav">
    <a href="../">Home</a>
    <router-link to="/">Pronunciation</router-link>
  </div>
  <router-view/>
</template>

<style lang="scss">
body{
  background-color: #F0EFE9;
  height: 100vh;
}
#app {
  height: 100vh;
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}

#nav {
  width: 100%;
  position: absolute;
  display: sticky;
  top: 0px;
  padding: 15px;

  a {
    font-weight: bold;
    // color: #2c3e50;
    margin-right: 15px;
    &.router-link-exact-active {
      border-bottom: 1px solid;
      // color: #42b983;
    }
  }
}
</style>
