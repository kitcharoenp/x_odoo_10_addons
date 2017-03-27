odoo.x_hr_holidays = function(instance) {
    var _t = instance.web._t,
    _lt = instance.web._lt;
    var QWeb = instance.web.qweb;

    instance.web_calendar.CalendarView.include({

        /**
         * overide get_event_data function changed date_start_day,
         * date_stop_day to 8:00 and 17:00
         */
        get_event_data: function(event) {
            var date_start_day;
            var date_stop_day;
            var diff_seconds;

            // Normalize event_end without changing fullcalendars event.
            var data = {
                name: event.title
            };

            var event_end = event.end;
            //Bug when we move an all_day event from week or day view, we don't have a dateend or duration...
            if (event_end === null) {
                var m_date = moment(event.start).add(2, 'hours');
                event_end = m_date.toDate();
            }

            if (event.allDay) {
                // Sometimes fullcalendar doesn't give any event.end.
                if (event_end === null || _.isUndefined(event_end)) {
                    event_end = new Date(event.start);
                }
                if (this.all_day) {
                    date_start_day = new Date(Date.UTC(event.start.getFullYear(),event.start.getMonth(),event.start.getDate()));
                    date_stop_day = new Date(Date.UTC(event_end.getFullYear(),event_end.getMonth(),event_end.getDate()));
                }
                else {
                    date_start_day = new Date(event.start.getFullYear(),event.start.getMonth(),event.start.getDate(),8);
                    date_stop_day = new Date(event_end.getFullYear(),event_end.getMonth(),event_end.getDate(),17);
                }
                data[this.date_start] = time.datetime_to_str(date_start_day);
                if (this.date_stop) {
                    data[this.date_stop] = time.datetime_to_str(date_stop_day);
                }
                diff_seconds = Math.round((date_stop_day.getTime() - date_start_day.getTime()) / 1000);

            }
            else {
                data[this.date_start] = time.datetime_to_str(event.start);
                if (this.date_stop) {
                    data[this.date_stop] = time.datetime_to_str(event_end);
                }
                diff_seconds = Math.round((event_end.getTime() - event.start.getTime()) / 1000);
            }

            if (this.all_day) {
                data[this.all_day] = event.allDay;
            }

            if (this.date_delay) {
                data[this.date_delay] = diff_seconds / 3600;
            }
            return data;
        },


    })
}
