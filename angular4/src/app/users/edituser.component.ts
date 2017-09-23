import { Component, Input, OnInit } from '@angular/core';
import { Router, Params, ActivatedRoute } from '@angular/router';
import { FormGroup, FormBuilder, Validators } from '@angular/forms';

import { UserService } from './user.service';
import { User, UserType } from './user';
import { RolesService } from '../services/roles.service';
import { RolesList } from 'app/classes/roles';
import { Select2OptionData } from 'ng2-select2/ng2-select2';

import 'rxjs/add/operator/switchMap';
import { VendorService } from "../services/vendor.service";
import {ValidationService} from "../directives/form-validations/validation.service";
import { GlobalsService } from 'app/services';
@Component({
    templateUrl: './adduser.component.html'
})
export class EditUserComponent implements OnInit {
    userId: number;
    user: User;
    userForm: FormGroup;
    errorMessage: string = '';
    title = 'Edit User';
    roleslist: any;
    selectedVal: any;
    select2Options: any = {
        theme: 'bootstrap'
    };
    private vendorList: any
    private vendorListValue: any = {}
    private showpagecontent: boolean
    private showvendorCategoryStatus: boolean = false
    select2DefaultData: UserType = new UserType();
    private tempvendorList: any
    private checknameErrorMsg: any;
    private showVendorDetails: boolean = false
    private isreadonly: boolean = true
    private vendorListArrayValue
    private userData;
    private regionArray=[];
    constructor(private router: Router,
        private route: ActivatedRoute,
        private userService: UserService,
        private fb: FormBuilder,
        private rolesService: RolesService, private vendorservice: VendorService, private gsService: GlobalsService) {
            this.gsService.user$.subscribe(data=> this.userData = data);
        };

    ngOnInit(): void {
        this.buildForm();
        //this.rolesService.getRolesList().subscribe(roleslist => { this.roleslist = roleslist; })
        this.userService.getUserTypeList().subscribe(select2DefaultData => { this.select2DefaultData = select2DefaultData; })
        this.vendorservice.getUsersVendors().then(vendorlistresult => {
            let tempvendorlist = []
            this.vendorListArrayValue = vendorlistresult;
            if ((this.vendorListArrayValue.super_user == true || this.userData.user_type == 'R') && vendorlistresult.data.length > 1) {
                this.userForm.controls['vendorCategory'].setValidators([ValidationService.nonEmptylistValidator]);
                this.userForm.controls['vendorCategory'].updateValueAndValidity();
            }
            if (vendorlistresult.data.length > 1) {
                this.showVendorDetails = true;
            }
            if (vendorlistresult.super_user == true && vendorlistresult.data.length != 0) {
                let vendoraliesobject = { 'id': -1, 'text': 'All' }
                tempvendorlist.push(vendoraliesobject);
            }
            for (let vendorobject of vendorlistresult.data) {
                let vendoraliesobject = { 'id': vendorobject.vendor_id, 'text': vendorobject.vendor_name }
                tempvendorlist.push(vendoraliesobject);
            }
            this.vendorList = tempvendorlist
            this.tempvendorList = tempvendorlist
        })
        this.showpagecontent = true
        this.route.params.subscribe(x => this.userId = +x['id']);
        this.rolesService.getRolesList().subscribe(roleslist => {
            this.roleslist = roleslist;
            this.route.params
                .switchMap((params: Params) => this.userService.getUser(+params['id']))
                .subscribe(user => {
                    this.user = user;
                   localStorage.setItem('username', this.user.username);
                    if (this.user.roleId != '') {
                        let roles = [];
                        for (let role of this.roleslist) {
                            for (let clientRole of this.user.vendorCategory.split(',')) {
                                if (role['id'] == clientRole) {
                                    roles.push(role);
                                }
                            }
                        }
                        this.user.roleId = roles;
                    } else {
                        this.user.roleId = [];
                    }
                    if (this.user.vendorCategory != '') {
                        let selectedvendors = [];
                        for (let vendorobject of this.user.vendorCategory) {
                            let vendoraliesobject = { 'id': vendorobject.vendor_id, 'text': vendorobject.vendor_name }
                            selectedvendors.push(vendoraliesobject);
                        }
                        this.user.vendorCategory = selectedvendors;

                    }
                    else {
                        this.user.vendorCategory = []
                    }
                    (<FormGroup>this.userForm).patchValue(this.user);
                    if (this.user.user_type !== 'R') {
                        this.showvendorCategoryStatus = true;
                    }
                    else {
                        this.showvendorCategoryStatus = false
                        //this.userForm.controls['vendorCategory'].clearValidators()
                    }
                });
        });

    }


    buildForm(): void {
        this.userForm = this.fb.group(
            {
                'username': ['', [
                    Validators.required
                ]],
                'email': ['', [
                    Validators.required, ValidationService.emailValidator
                ]],
                'employee_id':['', Validators.required],
                'firstName': ['',[
                    Validators.required
                ]],
                'lastName': ['', [
                    Validators.required
                ]],
                'address': [''],
                'description': [''],
                'location': [''],
                'vendorCategory': [''],
                'user_type': [''],
                'roleId': ['',[
                    Validators.required
                ]]
            }
        );
        this.userForm.valueChanges.subscribe(data => this.onValueChanged(data));
        this.onValueChanged();
    }

    onValueChanged(data?: any) {
        const form = this.userForm;

        const name = form.get('username');
        if (name && name.dirty && !name.valid) {
            for (const key in name.errors) {
                this.errorMessage += " Name is " + key
            }
        }

        const lastName = form.get('lastName');
        if (lastName && lastName.dirty && !lastName.valid) {
            for (const key in lastName.errors) {
                this.errorMessage += " Last name is " + key
            }
        }
    }

    submitForm(f): boolean {
        this.user = this.userForm.value;
        this.user.id = this.userId;   // Copy the id as its overwritten above
        let roleArr = [];
        let roleStr: string;
        for (let role of this.user.roleId) {
            roleArr.push(role.id);
        }
        roleStr = roleArr.join(',');
        this.user.region=this.regionArray;
        this.user.roleId = roleStr;
        this.user.user_type = this.selectedVal;
        let vendorArr = [];
        this.user.vendorCategory = vendorArr.join(',')
        this.userService.updateUser(this.user)
            .subscribe(user => {
                this.errorMessage = null;
                this.user = user;
                this.router.navigate(['/app/users']);
            },
            error => this.errorMessage = error);
        return false;
    }

    private value: any = {};
    private _disabledV: string = '0';
    private disabled: boolean = false;

    public selected(value: any): void {
        console.log('Selected value is: ', value);
    }

    public removed(value: any): void {
        console.log('Removed value is: ', value);
    }

    public typed(value: any): void {
        console.log('New search input: ', value);
    }

    public refreshValue(value: any): void {
        this.value = value;
    }

    public itemsToString(value: Array<any> = []): string {
        return value
            .map((item: any) => {
                return item.id;
            }).join(',');
    }

    getSelect2DefaultList() {
        return this.select2DefaultData;
    }

    select2Changed(e: any): void {
        if (e['value'] !== 'R') {
            this.showvendorCategoryStatus = true
        }
        else {
            this.showvendorCategoryStatus = false
        }
        this.selectedVal = e.value;
    }
    public vendorListselected(value: any): void {
        if (value.id == -1) {
            this.vendorList = []
            this.userForm.controls['vendorCategory'].setValue([{ 'id': -1, 'text': 'All' }])
        }
    }

    public vendorListremoved(value: any): void {
        if (value.id == -1) {
            this.vendorList = this.tempvendorList
        }
        console.log('Removed value is: ', value);
    }

    public vendorListtyped(value: any): void {
        console.log('New search input: ', value);
    }

    public refreshvendorlistValue(value: any): void {
        this.vendorListValue = value;
    }


}
