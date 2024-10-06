<script setup lang="ts">
import {ref, watch, onMounted, computed, nextTick} from 'vue';
import Flower from "@/components/Flower.vue";
import Recommendations from "@/components/Recommendations.vue";
import SongFeatureDialog from "@/components/SongFeatureDialog.vue";
import type { CSSProperties } from 'vue';
import Button from "primevue/button";
import { SongFeatureCategory } from '@/types/SongFeature';
import { Session } from '@/types/Session';
import { getSongFeatures } from '@/services/sessionService';

const props = defineProps<{
  session: Session,
}>();

const flowerData = computed(() => {
  return props.session.playlist.map(getSongFeatures);
});

//Zoom Function for the main visualization --> will be adapted at a later point
const zoomLevel = ref(1);
const minZoom = 0.3;
const maxZoom = 3;

const visualizationStyle = ref({
  transform: `scale(${zoomLevel.value})`,
  transformOrigin: 'bottom left',
});

const isScrollEnabled = ref(false);

function zoomIn() {
  zoomLevel.value = Math.min(zoomLevel.value + 0.1, maxZoom)
  updateZoom();
}
function zoomOut() {
  zoomLevel.value = Math.max(zoomLevel.value - 0.1, minZoom);
  updateZoom();}

function updateZoom() {
  console.log('Updating Zoom:', zoomLevel.value);

  if (zoomLevel.value <1){
    visualizationStyle.value.transformOrigin = 'bottom left';
  } else {
    visualizationStyle.value.transformOrigin = 'top left';
  }

  visualizationStyle.value.transform = `scale(${zoomLevel.value})`;
  isScrollEnabled.value = zoomLevel.value > 1;

}
function adjustZoomToFitContainer() {
  const container = document.querySelector('.visualization-container');
  if (container) {
    const containerWidth = container.clientWidth;
    const containerHeight = container.clientHeight;

    const maxFlowerSize = 240;
    const numFlowers = flowerData.value.length;

    // Assuming a simple grid layout for calculating total size
    const totalWidth = maxFlowerSize * Math.sqrt(numFlowers);
    const totalHeight = maxFlowerSize * Math.sqrt(numFlowers);

    const requiredZoom = Math.min(
        containerWidth / totalWidth,
        containerHeight / totalHeight
    );

    zoomLevel.value = Math.min(requiredZoom, maxZoom);
    updateZoom();

    if (zoomLevel.value === minZoom) {
      (visualizationStyle.value as any).left = '0px';
      (visualizationStyle.value as any).bottom = '0px';
    }
  }
}

watch(flowerData, () => {
  const flowerCount = flowerData.value.length;

  //needs to be adapted once layout is correct//
  if (flowerCount > 10) {
    zoomLevel.value = minZoom;
    updateZoom();
  }
}, { immediate: true });

// Define a grid size and positions for flowers
const gridSize = 80;
const maxVerticalMoves = 3;

let containerWidth = 0;
let containerHeight = 0;

const gridPositionToScreenPositionDeltaX = 100;
const gridPositionToScreenPositionDeltaY = 150;
let lastVerticalDirection = 0;
let currentX = 0;
let currentY = Math.floor(Math.random() * gridSize * maxVerticalMoves); //Random vertical placement for the first flower
let verticalNrFlowers = 1; //Nr of flowers vertically


const generateNextRandomGridPosition = () => {
  const stayInColumn = Math.random() > 0.5; //Decide whether to stay in same column or move to right
  const maxStack = (currentY <= gridSize || currentY >= gridSize * (maxVerticalMoves-1)) ? 3 : 2; // Determine maximum vertical based on currentY position

  if (stayInColumn && verticalNrFlowers < maxStack) {
    let verticalDirection = lastVerticalDirection;

    if (lastVerticalDirection === 1) {
      verticalDirection = 1;
    } else if (lastVerticalDirection === -1) {
      verticalDirection = -1;
    } else {
      if (currentY <= gridSize) { // If currentY too close to top, next flower will be placed down
        verticalDirection = 1;
      } else if (currentY >= gridSize * maxVerticalMoves) { // If currentY too close to bottom, next flower will be placed up
        verticalDirection = -1;;
      } else {
        verticalDirection = Math.random() > 0.5 ? 1 : -1;
      }
    }
    lastVerticalDirection = verticalDirection
    const verticalMove = verticalDirection * gridSize * (Math.random() > 0.5 ? 1.5 : 2);
    currentY += verticalMove;
    verticalNrFlowers++;
    return {x: currentX, y: currentY};

  } else {
    verticalNrFlowers = 0;
    const horizontalMove = gridSize * (Math.random() > 0.5 ? 1.5 : 2);
    currentX += horizontalMove;
    verticalNrFlowers = 1;

    lastVerticalDirection = 0;

    // Define first currentY, when moved horizontally
    const randomStartPositions = [0, gridSize * maxVerticalMoves, gridSize * Math.floor(maxVerticalMoves / 2)];
    currentY = randomStartPositions[Math.floor(Math.random() * randomStartPositions.length)];

    return { x: currentX, y: currentY };
  }
}

// Assign positions randomly
const generateRandomGridPositions = (flowerCount: number) => {
  const positions = [];

  for (let i = 0; i < flowerCount; i++) {
    if (i == 0) {
      positions.push({ x:0, y:currentY}); // First flower starts in first column and random Y
    } else {
      positions.push(generateNextRandomGridPosition());
    }
  }

  return positions;
};

const gridPositions = ref(generateRandomGridPositions(flowerData.value.length));

const recommendationsContainer = ref(null);

// Position the next recommendations close to the last song
const recommendationsStyle = computed(() => {

  const distanceToLastSong = 50;

  let x = 0;
  let y = 0;

  if (gridPositions.value.length !== 0) {
    const lastSongPosition = gridPositions.value[gridPositions.value.length - 1];
    x = lastSongPosition.x + distanceToLastSong;
    y = lastSongPosition.y;
  }

  return {
    left: `${x + gridPositionToScreenPositionDeltaX}px`,
    top: `${y + gridPositionToScreenPositionDeltaY}px`,
  };

});

const flowerStyles = computed(() => {
  for (let i = gridPositions.value.length; i < flowerData.value.length; i++) {
    gridPositions.value = [...gridPositions.value, generateNextRandomGridPosition()];
  }

  return gridPositions.value.map((position) => {
    const { x, y } = position;

    return {
      position: 'absolute',
      left: `${x + gridPositionToScreenPositionDeltaX}px`,
      top: `${y + gridPositionToScreenPositionDeltaY}px`,
    };
  });
});


const scrollRecommendationsIntoView = async () => {
  await nextTick();
  recommendationsContainer.value?.firstChild.scrollIntoView({behavior: "smooth", block: "start"});
};

onMounted(() => {
  //Container Dimensions
  const container = document.querySelector('.visualization-container');
  if (container) {
    containerWidth = container.clientWidth;
    containerHeight = container.clientHeight;
  }

  //Zoom to fit container
  adjustZoomToFitContainer(); // Fit visualization to container size on mount
  updateZoom();

  const scrollWrapper = document.querySelector('.scroll-wrapper') as HTMLElement;
  const visualization = document.querySelector('.visualization') as HTMLElement;

  // Scroll to the bottom left
  if (scrollWrapper && visualization) {
    // Set the scroll position to the bottom
    scrollWrapper.scrollTop = scrollWrapper.scrollHeight - scrollWrapper.clientHeight;

    // Set the scroll position to the left
    scrollWrapper.scrollLeft = 0;
  }
});

const currentSelectedFeature = ref(null);
const showFeaturesInformation = ref(false);
const onPetalClick = (index: number, featureCategory: SongFeatureCategory) => {
  currentSelectedFeature.value = {
    index,
    featureCategory
  };
  showFeaturesInformation.value = true;
};
</script>

<template>
  <div class = main-visualization>
    <div class="zoom-controls">
      <button @click="zoomIn">+</button>
      <button @click="zoomOut">-</button>
    </div>
    <div class= visualization-container>
      <div class="scroll-wrapper">
        <div class="visualization" :style="visualizationStyle">
          <!-- Loop through each flower and apply the styles -->
          <div
              v-for="(flower, index) in flowerData"
              :key="index"
              :style="flowerStyles[index]"
              class="flower-wrapper"
          >
            <Flower
                :features="flower"
                :circleRadius="40"
                @onPetalClick="(featureCategory) => onPetalClick(index, featureCategory)"
            />
          </div>
            <Recommendations
              v-if="session.isRunning"
              :sessionId="session.id"
              :key="flowerData.length"
              class="recommendations"
              :style="recommendationsStyle"
              @recommendationsLoaded="scrollRecommendationsIntoView()"
            />
        </div>
      </div>
    </div>
    <SongFeatureDialog
      v-model:visible="showFeaturesInformation"
      :flowerData="flowerData"
      :currentSelectedFeature="currentSelectedFeature"
    />
  </div>
</template>

<style scoped>
.main-visualization {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.visualization-container{
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.visualization {
  display: grid;
  grid-template-columns: repeat(auto-fill, 80px);
  grid-template-rows: repeat(auto-fill, 80px);
  width: 100%;
  height: 100%;
  position: relative;
  overflow: visible;
}

.scroll-wrapper {
  position: absolute;
  top: 0;
  left: 0;
  right: 30px;
  bottom: 0;
  overflow-x: auto;
  overflow-y: auto;
  padding-left: 10px;
  padding-bottom: 10px;
}

.type2 .scroll-wrapper::-webkit-scrollbar {
  width: 5px;
  height: 5px;
  background-color: var(--backcore-color2);
  border-radius: 12px;
}

.type2 .scroll-wrapper::-webkit-scrollbar-thumb {
  background-color: var(--backcore-color3);
  border-radius: 12px;
}

.type2 .scroll-wrapper::-webkit-scrollbar-thumb:hover {
  background-color: var(--backcore-color1);
}

.type2 .scroll-wrapper::-webkit-scrollbar-corner {
  background-color: var(--backcore-color1);
}

.type2 .zoom-controls {
  position: absolute;
  top: 40px;
  right: 10px;
  z-index: 10;
  display: flex;
  flex-direction: column;
  gap: 5px;
}
.type2 .zoom-controls button {
  width: 20px;
  height: 20px;
  background-color: var(--backcore-color2);
  color: var(--font-color);
  border: none;
  border-radius: 5px;
  cursor: pointer;
}
.flower {
  transition: all 0.3s ease;
}
.flower-wrapper {
  position: absolute;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 160px;
  height: 160px;
  transform: translate(-50%, -50%);
}
.recommendations {
  position: relative;
  transform: translate(0%, -50%);
  transition: all 0.3s ease;
  margin: auto;
}
</style>