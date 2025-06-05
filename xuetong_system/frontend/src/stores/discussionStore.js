import { defineStore } from 'pinia';
import apiClient from '../services/apiClient';
// import router from '../router'; // Not typically needed for data stores unless actions cause global navigation

export const useDiscussionStore = defineStore('discussion', {
    state: () => ({
        currentDiscussionThread: null, // Structure: { post_id, ..., author: {}, replies: [{ post_id, ..., author:{}, reply_count (for replies to this reply) }] }

        isLoadingThread: false,
        fetchThreadError: null,

        isPostingReply: false,
        postReplyError: null,
    }),
    getters: {
        getThread: (state) => state.currentDiscussionThread,
        // Example: get a specific reply from the thread
        // getReplyById: (state) => (replyId) => {
        //   if (!state.currentDiscussionThread || !state.currentDiscussionThread.replies) return null;
        //   return state.currentDiscussionThread.replies.find(reply => reply.post_id === replyId);
        // },
    },
    actions: {
        async fetchDiscussionThread(postId) {
            this.isLoadingThread = true;
            this.fetchThreadError = null;
            this.currentDiscussionThread = null; // Clear previous thread
            try {
                // API endpoint GET /discussions/<post_id>/thread returns the post and its direct replies
                const response = await apiClient.get(`/discussions/${postId}/thread`);
                this.currentDiscussionThread = response.data;
            } catch (err) {
                const message = err.response?.data?.message || err.message || 'Failed to fetch discussion thread.';
                this.fetchThreadError = message;
                console.error(`Error fetching discussion thread for post ID ${postId}:`, message);
            } finally {
                this.isLoadingThread = false;
            }
        },

        async postReply(parentPostId, replyData) { // replyData = { content }
            this.isPostingReply = true;
            this.postReplyError = null;
            try {
                // API endpoint POST /discussions/<parent_post_id>/replies
                const response = await apiClient.post(`/discussions/${parentPostId}/replies`, replyData);
                const newReply = response.data;

                // If the current thread is for the parentPostId, add the new reply
                if (this.currentDiscussionThread && this.currentDiscussionThread.post_id === parentPostId) {
                    if (!this.currentDiscussionThread.replies) {
                        this.currentDiscussionThread.replies = [];
                    }
                    this.currentDiscussionThread.replies.push(newReply);
                    // Update reply count on the main post
                    this.currentDiscussionThread.reply_count = (this.currentDiscussionThread.reply_count || 0) + 1;

                }
                // If parentPostId is one of the currently displayed replies (for nested replies)
                // This part is more complex if we want to update nested replies reactively without a full re-fetch.
                // For now, we primarily handle replies to the main topic.
                // A full re-fetch is simpler if deep nesting updates are needed immediately:
                // else {
                //    await this.fetchDiscussionThread(this.currentDiscussionThread.post_id); // Re-fetch the whole thread
                // }
                // OR, if not viewing the parent thread, do nothing to local state for now.

                return { success: true, data: newReply };
            } catch (err) {
                const message = err.response?.data?.message || err.message || 'Failed to post reply.';
                this.postReplyError = message;
                console.error(`Error posting reply to post ID ${parentPostId}:`, message);
                return { success: false, error: message };
            } finally {
                this.isPostingReply = false;
            }
        },

        clearDiscussionThread() {
            this.currentDiscussionThread = null;
            this.fetchThreadError = null;
            this.postReplyError = null; // Also clear reply error related to this thread
        },

        clearPostReplyError() {
            this.postReplyError = null;
        }
    },
});
