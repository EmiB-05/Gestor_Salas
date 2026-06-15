var calendar = new FullCalendar.Calendar(
    document.getElementById('calendar'),
    {
        initialView: 'timeGridWeek',

        selectable: true,

        dateClick: function(info) {
            alert("Reservar: " + info.dateStr);
        },

        events: '/api/reservas'
    }
);

calendar.render();