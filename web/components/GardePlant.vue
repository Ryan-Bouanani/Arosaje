<script>
import { ApiService } from '@/services/api';

export default {
  name: 'GardePlant',
  props: {
    plantName: {
      type: String,
      required: true
    },
    plantPhoto: { // Nouvelle prop pour recevoir l'URL de la photo
      type: String,
      required: true
    }
  },
  data() {
    return {
      photo: null, 
      photoPreview: null, 
      gardeData: {
        name: this.plantName,  // Préreemplissage du nom de la plante
        soins: '',
        location: '', // Localisation
        startDate: '', // Date de début
        endDate: '' // Date de fin
      },
      errorMessage: "" 
    };
  },
  watch: {
    photo(newValue) {
      if (!newValue) {
        this.photoPreview = null;
        this.errorMessage = "";
      }
    }
  },
  methods: {
    async handleSubmit() {
      try {
        const response = await ApiService.createPlantCare({
          plant_id: 1,  // Remplacez par l'ID de la plante, si disponible
          caretaker_id: null,  // Optionnel si vous avez un caretaker_id à transmettre
          start_date: this.gardeData.startDate,
          end_date: this.gardeData.endDate,
          location: this.gardeData.location,
          owner_id: this.gardeData.owner_id
        });

        if (response.success) {
          alert('Plante ajoutée à la garde avec succès !');
          this.closeModal();
        } else {
          alert(`Erreur: ${response.error}`);
        }
      } catch (error) {
        alert(`Erreur : ${error}`);
      }
    },
    closeModal() {
      this.$emit('close');
    }
  }
};
</script>

<template>
  <v-card class="modal-content pa-4 max-w-md mx-auto">
    <div class="max-w-md mx-auto p-4">
      <div class="flex items-center mb-6">
        <button @click="closeModal" class="mr-2">
          <span class="text-xl">&larr;</span>
        </button>
        <h1 class="text-xl font-medium">Ajouter une plante à la garde - A'rosa-je</h1>
      </div>

      <div class="mb-6">
        <h2 class="text-lg mb-3">Faites garder votre plante !</h2>

        <div v-if="plantPhoto" class="mt-4 mb-4 image-preview">
          <img :src="plantPhoto" alt="Photo de la plante" class="preview-img" />
        </div>

        <form @submit.prevent="handleSubmit">
          <v-text-field
            v-model="gardeData.name"
            label="Nom de la plante"
            placeholder="Ex: Ficus lyrata"
            variant="outlined"
            rounded="lg"
            density="comfortable"
            class="mb-4"
            :disabled="true"
          ></v-text-field>

          <v-textarea
            v-model="gardeData.soins"
            label="Soins spécifiques"
            placeholder="Entrez les soins nécessaires pour votre plante"
            variant="outlined"
            rounded="lg"
            density="comfortable"
            class="mb-4"
            rows="3"
          ></v-textarea>

          <v-text-field
            v-model="gardeData.location"
            label="Localisation"
            placeholder="Entrez la localisation de la plante"
            variant="outlined"
            rounded="lg"
            density="comfortable"
            class="mb-4"
          ></v-text-field>

          <v-text-field
            v-model="gardeData.startDate"
            label="Date de début"
            type="date"
            variant="outlined"
            rounded="lg"
            density="comfortable"
            class="mb-4"
          ></v-text-field>

          <v-text-field
            v-model="gardeData.endDate"
            label="Date de fin"
            type="date"
            variant="outlined"
            rounded="lg"
            density="comfortable"
            class="mb-4"
          ></v-text-field>

          <v-btn type="submit" color="green" class="white--text w-full">
            Ajouter la plante à la garde
          </v-btn>
        </form>
      </div>
    </div>
  </v-card>
</template>

<style scoped>
.modal-content {
  background-color: white !important;
  border-radius: 10px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
}

.image-preview {
  display: flex;
  justify-content: center;
  align-items: center;
  max-width: 100%;
  overflow: hidden;
}

.preview-img {
  max-width: 100%;
  max-height: 200px;
  object-fit: contain;
  border-radius: 8px;
  margin-top: 10px;  
  margin-bottom: 10px; 
}
</style>
