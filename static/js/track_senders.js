// Create a Set to keep track of unique senders
export let shownSenders = new Set(JSON.parse(localStorage.getItem('shownSenders')) || []);
// Create a Set to keep track of unique room_ids
export let shownRooms = new Set(JSON.parse(localStorage.getItem('shownRooms')) || []);
