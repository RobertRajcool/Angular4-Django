import { Component, OnInit, ViewEncapsulation } from '@angular/core';
import { NotificationActionsService, NotificationGroupsService } from 'app/services';
import { NotificationAction, NotificationGroup } from 'app/classes';
import { Router, NavigationExtras } from '@angular/router';

@Component({
    selector: 'app-notification-actions',
    encapsulation: ViewEncapsulation.Emulated,
    templateUrl: './notification-actions.component.html',
    styleUrls: ['./notification-actions.component.scss']
})
export class NotificationActionsComponent implements OnInit {
    actions: Array<Array<string>> = [];
    nfAction: NotificationAction;
    unmappedUfGroups: Array<NotificationGroup> = [];
    selectedAction: string = 'initial';
    selectedGroup: number;

    constructor(
        private nfaService: NotificationActionsService, 
        private nfgService: NotificationGroupsService,
        private router: Router
    ) { }

    ngOnInit() {
        this.changeAction('initial');
    }

    // Change current selected action
    changeAction(action: string) {
        this.selectedAction = action;
        this.selectedGroup = null;
        this.fetchData();
    }

    // Mapping
    map() {
        if (this.selectedAction && this.selectedGroup) {
            this.nfaService.mapGroup(this.selectedAction, this.selectedGroup)
                .subscribe(
                Result => {
                    this.updateValues(Result);
                },
                Error => console.log(Error)
                );
        }
    }

    // Remove group from NotificationAction
    unMap(group_id: number) {
        this.nfaService.unMap(this.nfAction.id, group_id)
            .subscribe(
            Result => this.updateValues(Result),
            Error => console.log(Error)
            );
    }

    // Get action details & unmapped groups list
    fetchData() {
        this.nfaService.getFetchActionInfo(this.selectedAction)
            .subscribe(
            Result => {
                this.updateValues(Result);
            },
            Error => console.log(Error)
            );
    }

    // Update local values
    updateValues(result: any) {
        this.nfAction = result['action_details'];
        this.unmappedUfGroups = result['unmapped_groups'];
        if (this.actions.length == 0) this.actions = result['actions'];
        if (this.selectedAction == 'initial') {
            if(result['action_details']) this.selectedAction = result['action_details']['action'];
            else this.selectedAction = result['actions'][0][0];
        }
    }

    navigate(id: number) {
        this.nfgService.updateDefaultShowGroupId(id);
        this.router.navigate(['/app/notification-groups']);
    }
}
