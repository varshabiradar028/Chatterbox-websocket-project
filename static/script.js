let socket;
let username;

const chat=document.getElementById("chat");
const typing=document.getElementById("typing");
const room=document.getElementById("room");

function joinChat(){

username=document.getElementById("username").value;

if(username==="") return;

document.querySelector(".login").style.display="none";
document.getElementById("chatSection").style.display="block";

socket=new WebSocket("ws://localhost:8000/ws");

socket.onopen=()=>{

socket.send(JSON.stringify({
type:"join",
username:username,
room:room.value
}));

};

socket.onmessage=(event)=>{

const data=JSON.parse(event.data);

const div=document.createElement("div");

if(data.type==="chat"){
div.innerHTML="<b>"+data.username+":</b> "+data.message;
}

if(data.type==="system"){
div.className="system";
div.innerText=data.message;
}

if(data.type==="typing"){
typing.innerText=data.username+" is typing...";
}

if(data.type==="stop_typing"){
typing.innerText="";
}

if(data.type==="users"){

const users=document.getElementById("users");

users.innerHTML="";

data.users.forEach(user=>{

const li=document.createElement("li");
li.innerText=user;

users.appendChild(li);

});

}

if(data.type!=="users"){
chat.appendChild(div);
chat.scrollTop=chat.scrollHeight;
}

};

}

function sendMessage(){

const msg=document.getElementById("msg").value;

if(msg==="") return;

socket.send(JSON.stringify({
type:"chat",
message:msg
}));

socket.send(JSON.stringify({
type:"stop_typing"
}));

document.getElementById("msg").value="";
}

document.getElementById("msg").addEventListener("input",()=>{

socket.send(JSON.stringify({
type:"typing"
}));

});

room.addEventListener("change",()=>{

socket.send(JSON.stringify({
type:"change_room",
room:room.value
}));

});