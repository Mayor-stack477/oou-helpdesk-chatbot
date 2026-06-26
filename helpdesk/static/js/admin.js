// ===============================
// OOU HELP DESK DASHBOARD
// ===============================

// Current Time
function updateTime(){

    const today = new Date();

    const options = {

        weekday:"long",

        year:"numeric",

        month:"long",

        day:"numeric",

        hour:"2-digit",

        minute:"2-digit",

        second:"2-digit"

    };

    const clock = document.getElementById("currentTime");

    if(clock){

        clock.innerHTML = today.toLocaleString("en-US", options);

    }

}

setInterval(updateTime,1000);

updateTime();


// Card Animation

const cards = document.querySelectorAll(".card");

cards.forEach((card,index)=>{

    card.style.opacity="0";

    card.style.transform="translateY(20px)";

    setTimeout(()=>{

        card.style.transition="0.5s";

        card.style.opacity="1";

        card.style.transform="translateY(0)";

    },index*200);

});


// Table Search

const searchInput=document.getElementById("searchTable");

if(searchInput){

searchInput.addEventListener("keyup",function(){

let value=this.value.toLowerCase();

let rows=document.querySelectorAll("table tbody tr");

rows.forEach(row=>{

row.style.display=row.innerText.toLowerCase().includes(value)
?"":"none";

});

});

}


// Sidebar Active Link

const links=document.querySelectorAll(".sidebar a");

links.forEach(link=>{

link.addEventListener("click",function(){

links.forEach(l=>l.classList.remove("active"));

this.classList.add("active");

});

});


// Welcome Message

console.log("OOU Help Desk Dashboard Ready");