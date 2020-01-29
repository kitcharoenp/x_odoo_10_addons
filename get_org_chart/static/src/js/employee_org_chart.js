odoo.define('get_org_chart.org_chart_button', function(require) {
    "use strict";

    var form_widget = require('web.form_widgets');

    var OrgChartButton = form_widget.WidgetButton.include({

        on_click: function() {
            var self = this
            self._super();

            self.peopleElement = document.getElementById("people");
            if (self.peopleElement && self.$el.hasClass('org-chart')) {
                var display = self.peopleElement.style.display;
                if (display === 'block') {
                    self.peopleElement.style.display = 'none';
                    return;
                } else if (display === 'none') {
                    self.peopleElement.style.display = 'block';
                    return;
                };

                self.employee_id = self.peopleElement.getAttribute('employee');
                self.getDatas();
            }
        },

        renderOrgChart: function(data) {
            var chartData = JSON.parse(data);
            var dataSource = chartData.dataSource;

            if (dataSource.length <= 1) {
                this.do_notify('No hierarchy position.');
                return;
            };

            var orgChart = new getOrgChart(this.peopleElement, {
                primaryFields: ["name", "job_id", "work_location", "work_email", "work_phone", "mobile_phone"],
                photoFields: ["image"],
                parentIdField: "parent_id",
                color: "black",
                scale: 0.5,
                linkType: "M",
                enableEdit: false,
                enableZoom: true,
                enableMove: true,
                theme: "OdooTheme",
                enableGridView: false,
                enableSearch: true,
                enableDetailsView: false,
                enableZoomOnNodeDoubleClick: false,
                expandToLevel: chartData.expandToLevel,
                dataSource: dataSource,
                customize: chartData.customize,
                clickNodeEvent: this.redirectNode,
                renderNodeEvent: this.renderNodHandler,
            });
            this.peopleElement.style.display = 'block';
        },

        getDatas: function() {
            return $.ajax({
                url: '/hr_employee/get_org_chart/' + this.employee_id,
                method: 'GET',
                data: {},
                success: $.proxy(this.renderOrgChart, this),
            });
        },

        renderNodHandler: function(sender, args) {
            for (var i = 0; i < args.content.length; i++) {
                if (args.content[i].indexOf("[reporters]") != -1) {
                    args.content[i] = args.content[i].replace("[reporters]", args.node.children.length);
                }
            }
        },

        redirectNode: function(sender, args) {
            var hash = location.hash;
            var index = hash.indexOf("&");
            var first_hash_attr = hash.substr(1, index - 1);
            if (args.node.id && first_hash_attr.match(/id=*/)) {
                hash = hash.substr(0, 1) +
                    "id=" + args.node.id + hash.substr(index);
                location.hash = hash;
            };

        },
    });

    return {
        OrgChartButton: OrgChartButton
    };

});