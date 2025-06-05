import { defineStore } from 'pinia';
import apiClient from '../services/apiClient';
import { ElMessage } from 'element-plus'; // For user feedback

export const useProgressStore = defineStore('progress', {
    state: () => ({
        // Stores progress for all materials in the currently viewed/active course
        currentCourseMaterialProgressList: [],

        isLoadingMaterialProgressList: false, // For loading the list for a course
        fetchMaterialProgressListError: null,

        // Tracks loading state for individual material updates, keyed by material_id
        isUpdatingProgress: {},
        // Tracks errors for individual material updates, keyed by material_id
        updateProgressError: {},
    }),
    getters: {
        getMaterialProgressForCurrentCourse: (state) => state.currentCourseMaterialProgressList,

        // Get completion status for a specific material in the current list
        getCompletionStatusByMaterialId: (state) => (materialId) => {
            const progressItem = state.currentCourseMaterialProgressList.find(p => p.material_id === materialId);
            return progressItem ? progressItem.is_completed : false;
        },

        // Get progress percentage for a specific material
        getProgressPercentageByMaterialId: (state) => (materialId) => {
            const progressItem = state.currentCourseMaterialProgressList.find(p => p.material_id === materialId);
            return progressItem ? progressItem.progress_percentage : 0;
        },

        // Check if a specific material's progress is currently being updated
        isMaterialProgressUpdating: (state) => (materialId) => {
            return !!state.isUpdatingProgress[materialId];
        },

        // Get update error for a specific material
        getMaterialUpdateError: (state) => (materialId) => {
            return state.updateProgressError[materialId] || null;
        }
    },
    actions: {
        async fetchMaterialProgressForCourse(courseId) {
            this.isLoadingMaterialProgressList = true;
            this.fetchMaterialProgressListError = null;
            this.currentCourseMaterialProgressList = []; // Clear previous list
            try {
                const response = await apiClient.get(`/courses/${courseId}/my-material-progress`);
                this.currentCourseMaterialProgressList = response.data;
            } catch (err) {
                const message = err.response?.data?.message || err.message || 'Failed to fetch material progress for course.';
                this.fetchMaterialProgressListError = message;
                console.error(`Error fetching material progress for course ID ${courseId}:`, message);
            } finally {
                this.isLoadingMaterialProgressList = false;
            }
        },

        async markMaterialProgress(materialId, isCompleted) {
            // Note: courseId is not strictly needed for the API call to /materials/:id/progress,
            // but it's useful if we want to update the specific course's progress list.
            this.isUpdatingProgress[materialId] = true;
            // Clear previous error for this specific material
            if (this.updateProgressError[materialId]) {
                delete this.updateProgressError[materialId];
            }

            try {
                const response = await apiClient.post(`/materials/${materialId}/progress`, { is_completed: isCompleted });
                const updatedProgressRecord = response.data;

                // Update the specific material's progress in currentCourseMaterialProgressList
                const index = this.currentCourseMaterialProgressList.findIndex(p => p.material_id === materialId);
                if (index !== -1) {
                    // Ensure all fields from response are updated, especially if backend returns more than just is_completed
                    this.currentCourseMaterialProgressList.splice(index, 1, {
                        ...this.currentCourseMaterialProgressList[index], // keep existing fields like material_title
                        is_completed: updatedProgressRecord.is_completed,
                        progress_percentage: updatedProgressRecord.progress_percentage,
                        last_learn_time: updatedProgressRecord.last_learn_time,
                    });
                } else {
                    // If material was not in list (e.g., list not fetched yet, or new material),
                    // we might add it, or rely on a re-fetch of the list by the component.
                    // For simplicity, we primarily update if it's already in the list.
                    // A component could call fetchMaterialProgressForCourse after this if needed.
                    // Or, if the response contains material_title:
                    if (updatedProgressRecord.material_title) {
                         this.currentCourseMaterialProgressList.push(updatedProgressRecord);
                    }
                }
                ElMessage.success(`"${updatedProgressRecord.material_title || materialId}" 状态更新成功!`);
                return { success: true, data: updatedProgressRecord };
            } catch (err) {
                const message = err.response?.data?.message || err.message || 'Failed to update material progress.';
                this.updateProgressError[materialId] = message;
                console.error(`Error updating progress for material ID ${materialId}:`, message);
                ElMessage.error(message);
                return { success: false, error: message };
            } finally {
                this.isUpdatingProgress[materialId] = false;
            }
        },

        clearProgressForCourse() { // Renamed to be more generic as it clears the current list
            this.currentCourseMaterialProgressList = [];
            this.fetchMaterialProgressListError = null;
            this.isLoadingMaterialProgressList = false; // Reset loading state too
            this.isUpdatingProgress = {}; // Clear all individual loading states
            this.updateProgressError = {}; // Clear all individual errors
        },

        clearMaterialUpdateError(materialId) {
            if (this.updateProgressError[materialId]) {
                delete this.updateProgressError[materialId];
            }
        }
    },
});
