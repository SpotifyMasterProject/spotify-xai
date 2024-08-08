<template>
  <div class="type1">
    <div class="visualizer">
      <div :class="{'svg-container': true, 'svg-container-animation': startAnimation}" v-html="svgContent"></div>
      <div :class="{'text-overlay': true, 'text-overlay-animation': startAnimation}">
        <LogoIntroScreen :class="{'logo-animation': startAnimation}" />
      </div>
    </div>
  </div>
</template>

<script>
import LogoIntroScreen from "@/components/LogoIntroScreen.vue";
import svgContent from '@/assets/circle-music-soundwave.svg';

export default {
  name: 'StartScreen',
  components: {
    LogoIntroScreen
  },
  data() {
    return {
      svgContent,
      startAnimation: false,
    };
  },
  mounted() {
    setTimeout(() => {
      this.startAnimation = true;
      setTimeout(() => {
        this.$emit('animation-complete'); //notify transition
      }, 2000)
    }, 2000); // Wait for 3 seconds before starting the animation
  }
}
</script>

<style scoped>
.visualizer {
  position: relative;
  width: 80vw;
  height: 80vw;
}

.svg-container {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  transition: transform 2s ease-in-out;
}

.svg-container-animation {
  transform: scale(2); /* Zoom in the SVG */
}

.text-overlay {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 2em;
  transition: transform 2s ease-in-out;
}

.text-overlay-animation {
  transform: translate(-50%, -400%); /* Shift the text upward */
}

.logo-animation {
  transform: scale(0.8); /* Adjust both position and size */
  font-size: 3vw; /* Adjust font size during the animation */
  transition: transform 1s ease-in-out, font-size 1s ease-in-out;
}
</style>
