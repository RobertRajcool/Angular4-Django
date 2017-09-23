import { Component, OnInit, ViewEncapsulation, OnDestroy } from '@angular/core';
import { FormBuilder, FormGroup, FormControl, Validators } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
import { NotificationGroupsService, GlobalsService } from 'app/services';
import { NotificationGroup, EmailRecepients } from 'app/classes';
import { GetApiurl } from '../../parameters';
import { ValidationService } from 'app/directives';
import { Subscription } from 'rxjs/Subscription';

@Component({
    selector: 'app-notification-groups',
    encapsulation: ViewEncapsulation.Emulated,
    templateUrl: './notification-groups.component.html',
    styleUrls: ['./notification-groups.component.scss']
})
export class NotificationGroupsComponent implements OnInit {
    nfGroupList: Array<NotificationGroup> = [];
    nfGroupForm: FormGroup;
    action: string = 'Create';
    recipientOptions: Array<{
        id: string;
        text: string;
    }> = [];
    remoteConfig: any = {
        url: GetApiurl('users/search/'),
        searchField: 'first_name + last_name',
        debounceTime: 300,
        authentication: true,
        tokenId: 'id_token',
        tokenStorage: 'localStorage',
        idField: 'id',
        textField: 'full_name'
    };
    selectedForEdit: number = -1;
    defaultShowGroupIdSubscription: Subscription;
    formDefaults: Object = {
        'name': '',
        'description': '',
        'recipients': [],
        'non_user_recipients': []
    }

    constructor(
        private nfgService: NotificationGroupsService,
        private fb: FormBuilder,
        private gs: GlobalsService
    ) {
        // Building form
        this.nfGroupForm = this.fb.group({
            'name': [this.formDefaults['name'], Validators.required],
            'description': [this.formDefaults['description']],
            'recipients': [this.formDefaults['recipients']],
            'non_user_recipients': [this.formDefaults['non_user_recipients']]
        });
    }

    ngOnInit() {
        // Get Notification groups list
        this.nfgService.getNfGroups()
            .subscribe(
            List => {
                this.nfGroupList = List;

                // Subscribe router parameters
                this.defaultShowGroupIdSubscription = this.nfgService.defaultShowGroupId$.subscribe(
                    groupId => {
                        if (groupId && groupId >= 0) {
                            let nf_group_id: number = groupId;
                            let index: number = List.map((group) => group.id).indexOf(nf_group_id);
                            this.selectForEdit(index);

                            // reset defaultShowGroupId
                            this.nfgService.updateDefaultShowGroupId(null);
                        }
                    }
                )
            },
            Error => console.log(Error)
            )
    }
    // select NotificationGroup to edit & update form
    selectForEdit(index: number) {
        this.selectedForEdit = index;
        this.assignFormValues(this.nfGroupList[index])
        this.action = 'Edit';
    }

    // Set form control values from object
    assignFormValues(value: any) {
        for (let ctrl_name of Object.keys(this.nfGroupForm.controls)) {
            if (Object.keys(value).indexOf(ctrl_name) > 0) {
                this.nfGroupForm.controls[ctrl_name].setValue(value[ctrl_name]);
                this.nfGroupForm.controls[ctrl_name].updateValueAndValidity();
            }
        }
    }

    // Resetting form
    resetForm() {
        if (this.action == 'Create') {
            this.nfGroupForm.reset();
            this.nfGroupForm.patchValue(this.formDefaults);
            this.nfGroupForm.updateValueAndValidity();
            
        }
        else if (this.action == 'Edit') {
            this.assignFormValues(this.nfGroupList[this.selectedForEdit])
        }
    }

    // Discard editing
    discard() {
        this.action = 'Create';
        this.resetForm();
    }

    // Form submission
    submitForm() {
        if (this.action == 'Create') {
            this.nfgService.createNfGroup(this.nfGroupForm.value)
                .subscribe(
                Response => {
                    this.nfGroupList.push(Response);
                    this.resetForm();
                    this.gs.setToastMessage('Group created successfuly', 5000);
                },
                Error => {
                    console.log(Error);
                }
                );
        }
        else if (this.action == 'Edit') {
            let new_object = this.nfGroupList[this.selectedForEdit];
            Object.assign(new_object, this.nfGroupForm.value);
            this.nfgService.updateNfGroup(new_object)
                .subscribe(
                Response => {
                    this.nfGroupList[this.selectedForEdit] = Response;
                    this.selectedForEdit = -1;
                    this.action = 'Create';
                    this.resetForm();
                    this.gs.setToastMessage('Group updated successfuly', 5000);
                },
                Error => console.log(Error)
                );
        }
    }

    // Delete NotificationGroup
    delete() {
        let deleted_id = this.nfGroupList[this.selectedForEdit].id;
        this.nfgService.deleteNfGroup(deleted_id)
            .subscribe(
            Response => {
                this.nfGroupList = this.nfGroupList.filter(group => group.id != deleted_id);
                this.selectedForEdit = -1;
                this.action = 'Create';
                this.resetForm();
                this.gs.setToastMessage('Group deleted successfuly', 5000);
            },
            Error => console.log(Error)
            );
    }

    ngOnDestroy() {
        this.defaultShowGroupIdSubscription.unsubscribe();
    }
}
