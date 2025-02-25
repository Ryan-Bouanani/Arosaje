<script>
import { ApiService } from '@/services/api';

export default {
  name: 'GardePlant',
  props: {
    plantName: {
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
    validateFileExtension(event) {
      const file = event.target.files[0];

      if (!file) {
        this.photo = null;
        return;
      }

      const isValidExtension = /\.(jpg|jpeg|png)$/i.test(file.name);
      const isValidMimeType = file.type === 'image/jpeg' || file.type === 'image/png';

      if (!isValidExtension || !isValidMimeType) {
        this.errorMessage = "Seuls les fichiers JPG ou PNG sont autorisés.";
        this.photo = null;
        this.photoPreview = null;
      } else {
        this.errorMessage = "";
        this.photo = file;
        this.photoPreview = URL.createObjectURL(file);
      }
    },
    async handleSubmit() {
      if (!this.photo) {
        alert("Veuillez ajouter une photo valide avant de soumettre.");
        return;
      }

      try {
        const response = await ApiService.createGarde({
          name: this.gardeData.name,
          espece: this.gardeData.espece,
          description: this.gardeData.description,
          soins: this.gardeData.soins,
          location: this.gardeData.location,
          startDate: this.gardeData.startDate,
          endDate: this.gardeData.endDate,
          photo: this.photo
        });

        if (response.success) {
          alert('Plante ajoutée à la garde avec succès !');
          this.closeModal();
        } else {
          alert(`Erreur: ${response.error}`);
        }
      } catch (error) {
        alert("Une erreur est survenue lors de l'ajout de la plante à la garde.");
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

        <v-file-input
          label="Photo de la plante"
          accept="image/jpeg, image/png"
          show-size
          outlined
          rounded="lg"
          density="comfortable"
          v-model="photo"
          @change="validateFileExtension"
          class="mb-4"
        ></v-file-input>

        <p v-if="errorMessage" class="text-red-500 text-sm mt-1">{{ errorMessage }}</p>

        <div v-if="photoPreview" class="mt-4 mb-4 image-preview">
           <img :src="photoPreview" alt="Aperçu" class="preview-img" />
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
