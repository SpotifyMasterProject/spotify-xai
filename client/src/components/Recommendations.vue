<script setup lang="ts">
import {ref, onMounted, computed} from 'vue';
import Flower from "@/components/Flower.vue";
import { sessionService, getSongFeatures } from "@/services/sessionService";

const props = defineProps<{
  sessionId: string,
}>();

const recommendations = ref([]);
const flowerData = computed(() => {
  return recommendations.value.map(getSongFeatures);
});

const emit = defineEmits(['recommendationsLoaded']);

onMounted(async () => {
  recommendations.value = await sessionService.getRecommendations(props.sessionId);
  emit('recommendationsLoaded');
});


</script>
<template>
  <div>
    <div v-for="(flower, index) in flowerData" class="recommendations-wrapper">
      <div class="flower-wrapper">
        <Flower
          :circleRadius=30
          :features="flower" />
      </div>
      <div class="song-details-container">
        <div class="song-details">
          <strong>{{recommendations[index].trackName}}</strong>
          <p>{{recommendations[index].artists[0]}}</p>
        </div>
      </div>
    </div>
  </div>
</template>
<style scoped>
.flower-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100px;
  height: 100px;
}
.song-details-container {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  max-width: 200px;
  white-space: nowrap;
}
.song-details {
  overflow: hidden;
  text-overflow: ellipsis;
}
.recommendations-wrapper {
  display: flex;
  flex-direction: row;
}
</style>