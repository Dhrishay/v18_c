import { AccountMoveKanbanController } from "@account/views/account_move_kanban/account_move_kanban_controller";
import { patch } from "@web/core/utils/patch";

patch(AccountMoveKanbanController.prototype, {
    setup() {
        super.setup();
        var hide_for_dc = 'default_request_type' in this.props.context && this.props.context.default_request_type
        this.showUploadButton = !hide_for_dc && this.props.context.default_move_type !== 'entry' || 'active_id' in this.props.context;
    }
});
