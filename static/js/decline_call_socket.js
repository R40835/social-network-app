export const declinedCallSocket = new WebSocket(
    'ws://'
    + window.location.host
    + '/ws/notification/calls-declined/' // connect to the caller websocket given you are the callee
);  