odoo.define("get_org_chart.form_view", function(require) {
    "use strict";

    var FormView = require("web.FormView");
    FormView.include({

        load_record: function(record) {
            var self = this;
            self._super.apply(this, arguments);
            if (self.model == 'hr.employee') {
                this.append_org_chart(record);
            };
        },

        append_org_chart: function(record) {
            var self = this;
            var record_id = record.id;
            var employee = 'employee="' + record_id + '">';
            var $new_div = $('<div id="people" ' + employee);

            var $peopleDiv = self.$el.find('#people');
            var $formSheet = self.$el.find('.o_form_sheet');
            if (!$peopleDiv.length) {
                $peopleDiv = $new_div;
                $peopleDiv.appendTo($formSheet);
            } else if (record_id != $peopleDiv.attr('employee')) {
                $peopleDiv.replaceWith($new_div);
            };
        },

    });
});