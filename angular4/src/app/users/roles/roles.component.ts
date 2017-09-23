import { Component, OnInit, ViewEncapsulation, OnDestroy } from '@angular/core';
import { FormGroup, FormBuilder, Validators } from '@angular/forms';
import { RolesService, GlobalsService } from 'app/services';
import { Roles } from 'app/classes';
import { Subscription } from 'rxjs/Subscription';
import { ValidationService } from 'app/directives';

declare var jQuery: any;

@Component({
    selector: 'app-roles',
    templateUrl: './roles.component.html',
    styleUrls: ['./roles.component.scss'],
    encapsulation: ViewEncapsulation.None,
})
export class RolesComponent implements OnInit {
    roles: any = [];
    permissionList: Array<{
        text: string;
        name: string;
        checked: boolean;
    }> = [];
    errorMessage: string = '';
    rolesForm: FormGroup;
    createString: string = 'Create';
    editString: string = 'Edit';
    action = this.createString;
    selectedId: number;
    role: Roles = new Roles();
    selectedPermissions: Array<string> = [];
    subscriptions: Object = {};
    processing: boolean = false;

    constructor(
        private fb: FormBuilder,
        private roleService: RolesService,
        private gs: GlobalsService
    ) { }

    ngOnInit(): void {
        this.roleService.getRoles().subscribe(roles => { this.roles = roles; });

        // User details subscription
        this.subscriptions['userDetailsSubscription'] = this.gs.user$.subscribe(user => {
            if (user)
                user.accesses.forEach(access => {
                    this.permissionList.push({ text: access, name: access, checked: false });
                })
        });

        // Build role creation/modify form
        this.buildForm();
    }

    buildForm(): void {
        this.rolesForm = this.fb.group(
            {
                'alias': [this.role.alias, [Validators.required]],
                'description': [this.role.description],
                'accesses': ['', [ValidationService.nonEmptylistValidator]]
            }
        );

        // Listener to validate role alias
        this.subscriptions['formControlSubscription'] = this.rolesForm.controls['alias'].valueChanges.subscribe(alias => {
            this.validateAlias(alias);
        });
    }

    // Validates role alias
    validateAlias(newAlias: string) {
        let rolesList = this.roles.filter(role => role.id != this.selectedId);
        let presentAliases: Array<string> = rolesList.map(role => role.alias);

        if (newAlias && presentAliases.indexOf(newAlias.trim()) >= 0) {
            const alias = this.rolesForm.get('alias');

            if (alias) {
                let errors: Object = alias.errors;
                if (!errors) errors = {};
                errors['notUnique'] = 'Role name already exists, please choose another one.';
                alias.setErrors(errors);
            }
        }
    }

    submitForm(): boolean {
        this.processing = true;

        if (this.rolesForm.invalid) {
            return false;
        }

        this.role = this.rolesForm.value;
        this.role.id = this.selectedId;
        this.role.accesses = this.rolesForm.value.accesses.join(',');
        if (this.selectedId) {
            this.roleService.updateRole(this.role)
                .subscribe(role => {
                    this.gs.setToastMessage("Role updated", 3000);
                    this.resetView();
                    this.updateRoles(role);
                    this.processing = false;
                },
                error => {
                    this.errorMessage = error;
                    this.processing = false;
                });
        } else {
            this.roleService.createRole(this.role)
                .subscribe(role => {
                    this.gs.setToastMessage("Role created", 3000);
                    this.resetView();
                    this.roles.push(role);
                    this.processing = false;
                },
                error => {
                    this.errorMessage = error;
                    this.processing = false;
                });
        }

        return false;
    }

    updateRoles(role): void {
        for (var i = 0; i < this.roles.length; i++) {
            if (role.id == this.roles[i].id) {
                this.roles[i] = role;
                return;
            }
        }
    }

    resetView(): void {
        this.errorMessage = null;
        this.rolesForm.reset();
        this.rolesForm.controls['alias'].enable();
        this.selectedPermissions = [];
        this.selectedId = null;
        this.action = this.createString;
        for (var index = 0; index < this.permissionList.length; index++) {
            this.permissionList[index]['checked'] = false;
        }
    }

    handleSelect(event): void {

        let optionIndex = this.permissionList.map((permission) => permission['name']).indexOf(event.target.value);

        if (event.target.checked) {
            this.selectedPermissions.push(event.target.value);
            this.permissionList[optionIndex]['checked'] = true;
        } else {
            this.selectedPermissions.splice(this.selectedPermissions.indexOf(event.target.value), 1);
            this.permissionList[optionIndex]['checked'] = false;
        }
        this.rolesForm.controls['accesses'].setValue(this.selectedPermissions);
        this.rolesForm.controls['accesses'].markAsTouched();
        this.rolesForm.controls['accesses'].updateValueAndValidity();
    }

    editRole(role): void {
        let groups = role.accesses.split(',');
        this.selectedPermissions = [];

        for (var index = 0; index < this.permissionList.length; index++) {
            let permissionObject = this.permissionList[index];
            this.permissionList[index]['checked'] = false;
            if (groups.indexOf(permissionObject['name']) != -1) {
                this.permissionList[index]['checked'] = true;
                this.selectedPermissions.push(permissionObject['name']);
            }
        }

        this.rolesForm.controls['alias'].setValue(role.alias);
        this.rolesForm.controls['alias'].markAsTouched();
        this.rolesForm.controls['description'].setValue(role.description);
        this.rolesForm.controls['description'].markAsTouched();
        this.rolesForm.controls['accesses'].setValue(this.selectedPermissions);
        this.rolesForm.controls['accesses'].markAsTouched();
        this.action = this.editString;
        this.selectedId = role.id;

        // Disabling role name editing for Predefined Roles
        if (new RegExp("^Predefined/", "g").test(role.name)) this.rolesForm.controls['alias'].disable();
        else this.rolesForm.controls['alias'].enable();
    }

    // Restting form values
    resetForm() {
        if (!this.selectedId) {
            this.rolesForm.reset();
            this.rolesForm.controls['alias'].enable();
        }
        else {
            let index = this.roles.map(role => role.id).indexOf(this.selectedId);
            this.editRole(this.roles[index]);
        }
    }

    // Unsubscribe subscriptions on component destroy
    ngOnDestroy() {
        for (let subscriptionName in this.subscriptions) {
            this.subscriptions[subscriptionName].unsubscribe();
        }
    }

}
