css=''' 
<style>
    body {
        font-family: 'Arial', sans-serif;
        margin: 0;
        padding: 0;
        background-color: #f5f5f5;
    }

    .chat-container {
        max-width: 600px;
        margin: 20px auto;
        overflow: hidden;
    }

    .chat-message {
        overflow: hidden;
        margin-bottom: 10px;
        display: flex;
        align-items: flex-start;
    }

    .avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        overflow: hidden;
        margin-right: 10px;
    }

    .avatar img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }

    .message {
        padding: 10px;
        border-radius: 8px;
        max-width: 70%;
        word-wrap: break-word;
        background-color: #fff;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }

    /* Bot-specific styles */
    .Bot .message {
        background-color: #4CAF50;
        color: #fff;
    }

    /* User-specific styles */
    .User .message {
        background-color: #2196F3;
        color: #fff;
    }
</style>

'''

bot_tempalte='''
<div class="chat-message Bot"> 
   <div class="avatar">
    <img src="https://static.vecteezy.com/system/resources/previews/010/872/460/original/3d-ai-robot-icon-png.png">
   </div>
   <div class="message">{{MSG}}</div>
 </div>     
'''

user_tempalte='''
<div class="chat-message Bot"> 
   <div class="avatar">
    <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTubaKbhGn1J2S6XqDzHStAx2APA7OCAFPBX9kAU15Hbw&s">
   </div>
   <div class="message">{{MSG}}</div>
 </div>     
'''