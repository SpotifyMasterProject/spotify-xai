<script setup lang="ts">
import { computed, defineProps } from 'vue';
import { SongFeature, SongFeatureCategory } from '@/types/SongFeature';

const props = defineProps<{
  feature: SongFeature;
  center: number;
  circleRadius: number;
}>();

const rotation = computed(() => ((props.feature.category ?? 0) * 360 / 5));

const colorPalettes = {
  [SongFeatureCategory.DANCEABILITY]: ['#A1DBE8', '#A1DBE8', '#A1DBE8', '#A1DBE8', '#A1DBE8'],
  [SongFeatureCategory.ENERGY]: ['#8AB15F', '#8AB15F', '#8AB15F', '#8AB15F', '#8AB15F'],
  [SongFeatureCategory.SPEECHINESS]: ['#DED9BA', '#EEE8C4', '#F4EEC8', '#F8F2CD', '#FEFAE1'],
  [SongFeatureCategory.TEMPO]: ['#F99945', '#F99945', '#F99945', '#F99945', '#F99945'],
  [SongFeatureCategory.VALENCE]: ['#E3CAF7', '#E3CAF7', '#E3CAF7', '#E3CAF7', '#E3CAF7'],
} as const; // This makes the object keys and values readonly

const calculateEllipseArea = (width: number, height: number) => {
  return Math.PI * (width / 2) * (height / 2);
};

const generatePetalPath = (totalLength: number, totalWidth: number) => {
  const pathData: string[] = [];
  const sections = (props.feature.category !== undefined) ? 5 : 1;
  const totalArea = calculateEllipseArea(totalWidth, totalLength);

  // Calculate the area for each section (linear distribution)
  const sectionAreas = Array.from({ length: sections }, (_, i) => (totalArea / sections) * (i + 1));

  // Generate paths for each section
  sectionAreas.forEach((area, i) => {
    const normalizedValue = Math.sqrt((i + 1) / sections);
    const sectionHeight = totalLength * normalizedValue;
    const sectionWidth = Math.sqrt((area / Math.PI) * 5); // Calculate width based on area and height

    const controlOffset = sectionWidth / 2;
    const controlPoint1X = props.center - controlOffset;
    const controlPoint1Y = props.center - sectionHeight / 2;
    const controlPoint2X = props.center + controlOffset;
    const controlPoint2Y = props.center - sectionHeight / 2;
    const endX = props.center;
    const endY = props.center - sectionHeight;

    const path = `
      M ${props.center} ${props.center}
      Q ${controlPoint1X} ${controlPoint1Y},
        ${endX} ${endY}
      Q ${controlPoint2X} ${controlPoint2Y},
        ${props.center} ${props.center}
    `;
    pathData.push(path);
  });

  return pathData;
};

const petalPaths = computed(() => {
  const baseRadius = props.circleRadius; // Base radius is 40px
  const petalLength = baseRadius * props.feature.value * 2; // Petal length based on value
  const maxMidWidth = petalLength / 2; // Make the middle the broadest part

  return generatePetalPath(petalLength, maxMidWidth);
});

const petalColors = computed(() => {
  if (props.feature.category !== undefined) {
    return colorPalettes[props.feature.category];
  }

  return [null];
});


</script>

<template>
  <g :transform="`rotate(${rotation}, ${center}, ${center})`">
    <path
        v-for="(path, i) in petalPaths"
        :key="i"
        :d="path"
        :fill="petalColors[i]"
        stroke="rgba(255, 255, 255, 0.3)"
        :stroke-width="props.feature.category !== undefined ? 0.5 : 2.0"
    />
  </g>
</template>

<style scoped>
path {
  transition: fill 0.3s ease;
}
</style>