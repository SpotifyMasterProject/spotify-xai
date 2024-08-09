<template>
  <button
    class="start-blend">
    Start Blend
  </button>
</template>

<style scoped>
.start-blend {
  background-color: #6BA149;
  color: white;
  border: none;
  border-radius: 50%;
  padding: 1.5em 3em;
  width: 300px;
  height: 300px;
  font-size: 1.5em;
  font-weight: bold;
  font-style: italic;
  cursor: pointer;
  outline: none;
  transition: background-color 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
}
.start-blend:hover {
  background-color: #363636;
}
@media (max-height: 450px) {
  .start-blend {
    width: calc(40px + (200 * (100vh - 100px) / 350));
    height: calc(40px + (200 * (100vh - 100px) / 350));
    font-size: calc(1em + (0.5em * (100vh - 100px) / 350));
    border-radius: 50%;
  }
}

</style>