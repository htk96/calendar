document.addEventListener('DOMContentLoaded', function() {
    const calendarEl = document.getElementById('calendar');
    
    const calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay'
        },
        editable: true,
        selectable: true,
        
        select: function(info) {
            const title = prompt('일정을 입력하세요:');
            if (title) {
                fetch('/api/projects', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        title: title,
                        start_date: info.startStr,
                        end_date: info.endStr
                    })
                })
                .then(response => response.json())
                .then(data => {
                    calendar.addEvent({
                        title: title,
                        start: info.startStr,
                        end: info.endStr
                    });
                });
            }
            calendar.unselect();
        },
        
        eventClick: function(info) {
            if (confirm('이 일정을 삭제하시겠습니까?')) {
                fetch(`/api/projects/${info.event.id}`, {
                    method: 'DELETE'
                })
                .then(() => {
                    info.event.remove();
                });
            }
        },
        
        eventDrop: function(info) {
            fetch(`/api/projects/${info.event.id}`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    start_date: info.event.startStr,
                    end_date: info.event.endStr
                })
            });
        }
    });

    // 초기 데이터 로드
    fetch('/api/projects')
        .then(response => response.json())
        .then(data => {
            const events = data.results.map(item => ({
                id: item.id,
                title: item.properties.이름.title[0].text.content,
                start: item.properties.시작일.date.start,
                end: item.properties.종료일.date.start
            }));
            calendar.addEventSource(events);
        });

    calendar.render();
});