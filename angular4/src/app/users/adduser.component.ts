import { Component, OnInit, ViewEncapsulation } from '@angular/core';
import { Router } from '@angular/router';
import { FormGroup, FormBuilder, Validators, FormControl } from '@angular/forms';

import { User, UserType } from './user';
import { UserService } from './user.service';
import { RolesService } from '../services/roles.service';
import { RolesList } from 'app/classes/roles';
import { Select2OptionData } from 'ng2-select2/ng2-select2';
import { VendorService } from "../services/vendor.service";
import { ValidationService } from "../directives/form-validations/validation.service";
import { GlobalsService } from 'app/services';
import {Pipe, PipeTransform} from '@angular/core';
import { Angulartics2 } from 'angulartics2';

declare var jQuery: any;
@Pipe({name: 'keys'})
@Component({
    selector: '[add-user]',
    templateUrl: './adduser.component.html',
    encapsulation: ViewEncapsulation.Emulated,
    styleUrls: ['./users.component.scss']
})
export class
AddUserComponent implements OnInit {
    user: User = new User(-1, '', '', '', '', '', '', '', '', '', '');
    errorMessage: string = '';
    userForm: FormGroup;
    title = 'Add new user';
    roleslist: any;
    selectedVal: any;
    select2Options: any = {
        theme: 'bootstrap'
    };

    select2DefaultData: UserType = new UserType();
    private vendorList;
    private checknameErrorMsg;
    private isNameExist: boolean = false
    private tempvendorList;
    private vendorListValue: any = {}
    private showpagecontent: boolean
    private showvendorCategoryStatus: boolean = false
    private showVendorDetails: boolean = false
    private isreadonly: boolean = false
    private vendorListArrayValue;
    private userData;
    public vendorName;
    public region_details;
    public keyArray=[];
    public vendorCategory;
    public showEmployeDetails='True'
    public regionArray=[];
    public employeeBranchCode;
    public branchCodeArray=[];

    constructor(
        private userService: UserService,
        private router: Router,
        private fb: FormBuilder,
        private rolesService: RolesService,
        private vendorservice: VendorService,
        private gsService: GlobalsService,
        private angulartics2: Angulartics2
        ) {
        this.gsService.user$.subscribe(data=> this.userData = data);
    };

    ngOnInit(): void {
        jQuery('.adduserform').parsley();
        this.rolesService.getRolesList().subscribe(roleslist => {
            this.roleslist = roleslist;
        })
        this.userService.getUserTypeList().subscribe(select2DefaultData => { this.select2DefaultData = select2DefaultData; })
       /*  this.vendorservice.getUsersVendors().then(vendorlistresult => {
            this.vendorListArrayValue = vendorlistresult;
            if ((this.vendorListArrayValue.super_user == true || this.userData.user_type == 'R') && vendorlistresult.data.length > 1) {
                this.userForm.controls['vendorCategory'].setValidators([ValidationService.nonEmptylistValidator]);
                this.userForm.controls['vendorCategory'].updateValueAndValidity();
            }
            let tempvendorlist = []
            if (vendorlistresult.data.length > 1) {
                this.showVendorDetails = true;
            }
            if (vendorlistresult.super_user == true && vendorlistresult.data.length > 1) {
                let vendoraliesobject = { 'id': -1, 'text': 'All' }
                tempvendorlist.push(vendoraliesobject);
            }
            for (let vendorobject of vendorlistresult.data) {
                let vendoraliesobject = { 'id': vendorobject.vendor_id, 'text': vendorobject.vendor_name }
                tempvendorlist.push(vendoraliesobject);
            }
            this.vendorList = tempvendorlist;
            this.tempvendorList = tempvendorlist
        }) */
        this.buildForm();
        this.showpagecontent = true
    }


    buildForm(): void {
        this.userForm = this.fb.group(
            {
                'username': new FormControl('', [Validators.required, ValidationService.userNameValidator]),
                'email': [this.user.email, [
                    Validators.required, ValidationService.emailValidator
                ]],
                'employee_id':[this.user.employee_id],
                'firstName': [this.user.firstName, Validators.required],
                'lastName': [this.user.lastName, [
                    Validators.required
                ]],
                'address': [this.user.address],
                'description': [this.user.description],
                'location': [this.user.location],
                'vendorCategory': [this.user.vendorCategory],
                'user_type': [this.user.user_type],
                'roleId': [this.user.roleId, Validators.required],
                'region':[this.user.region]
            }
        );
        /*this.userForm.valueChanges.subscribe(data => this.onValueChanged(data));
        this.onValueChanged();*/
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
                this.errorMessage += " LastName is " + key
            }
        }

    }
    submitForm(f): boolean {
        this.user = this.userForm.value;
        this.user.user_type = this.selectedVal;
        let roleArr = [];
        for (let role of this.user.roleId) {
            roleArr.push(role.id);
        }
        let vendorArr = [];
        /*if (this.user.vendorCategory == '' && this.vendorList.length == 1 && (this.user.user_type == 'R' || this.vendorListArrayValue.super_user == true) ) {
            for (let vendordetails of this.vendorList) {
                vendorArr.push(vendordetails['id']);
            }
        } else {
            for (let vendordetails of this.user.vendorCategory) {
                vendorArr.push(vendordetails['id']);
            }
        }*/
        if(this.user.user_type == 'R') {
          for (let vendordetails of this.vendorCategory) {
            vendorArr.push(vendordetails['vendor_id'])
          }
        }

        this.user.region=this.branchCodeArray;
        this.user.roleId = roleArr.join(',');
        this.user.vendorCategory = vendorArr.join(',');

        if (this.userForm.valid) {
            this.userService.addUser(this.user)
                .subscribe(user => {
                    this.errorMessage = null;
                    this.user = user;
                    this.regionArray=[];

                    // For Google Analytics
                    this.angulartics2.eventTrack.next({
                        action: 'Created',
                        properties: {
                            category: 'Users',
                            label: user['user_type']
                        }
                    });

                    this.router.navigate(['/app/users']);

                },
                error => this.errorMessage = error);
            return false;
        } else {
           // error => this.userForm.errors = error;
            return false;
        }

    }

    private value: any = {};
    private _disabledV: string = '0';
    private disabled: boolean = false;

    public selected(value: any): void {
       // console.log('Selected value is: ', value);
    }

    public removed(value: any): void {
        //console.log('Removed value is: ', value);
    }

    public typed(value: any): void {
        //console.log('New search input: ', value);
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
      //  console.log('Removed value is: ', value);
    }

    public vendorListtyped(value: any): void {
        //console.log('New search input: ', value);
    }

    public refreshvendorlistValue(value: any): void {
        this.vendorListValue = value;
    }

    checkUsername(event) {
        event.preventDefault();
        this.userService.checkNameExist(event.target.value)
            .then(data => {
                if (data != '') {
                    this.checknameErrorMsg = 'Username already exists'
                    this.isNameExist = true;
                }
                else {
                    this.checknameErrorMsg = null
                    this.isNameExist = false;
                }
            });
    }

   //api call to get emloyee detaile
   eventListener(event:any,modal:any){
    let EmployeeCode=this.userForm.value.employee_id;
     this.userService.getEmployeeDetails(EmployeeCode)
       .then (data=>{
         //console.log(data)
            this.keyArray=[]
            this.vendorName=data['vendor_category'];
            this.region_details=data['employee_region'];
            this.vendorCategory=data['vendor_details'];
            this.employeeBranchCode=data['employee_branch_code']
              for (let key in this.region_details) {
                 this.keyArray.push({key: key, value: this.region_details[key]})
                 let value=this.region_details[key];
                  this.regionArray.push(value)
              }
              for (let value in this.employeeBranchCode){
                 let code=this.employeeBranchCode[value];
                 this.branchCodeArray.push(code)
              }

         if(data!=''){
            this.userForm = this.fb.group(
            {
                'username': new FormControl('', [Validators.required, ValidationService.userNameValidator]),
                'email': [data['employeeEmail'],[ Validators.required]],
                'employee_id':[data['employee_code'], [Validators.required]],
                'firstName': [data['employee_firstname'], [Validators.required]],
                'lastName': [data['employee_lastname'], [ Validators.required ]],
                'address': [this.user.address],
                'description': [this.user.description],
                'location': [this.user.location],
                'vendorCategory': [this.user.vendorCategory],
                'user_type': [this.user.user_type],
                'roleId': [this.user.roleId, Validators.required]
            });
         }
         else {
           jQuery('#myModal').modal('show');
            this.userForm = this.fb.group(
            {
                'username': new FormControl('', [Validators.required, ValidationService.userNameValidator]),
                'email': [this.user.email, [
                    Validators.required, ValidationService.emailValidator
                ]],
                'employee_id':[this.user.employee_id, Validators.required],
                'firstName': [this.user.firstName, Validators.required],
                'lastName': [this.user.lastName, [
                    Validators.required
                ]],
                'address': [this.user.address],
                'description': [this.user.description],
                'location': [this.user.location],
                'vendorCategory': [this.user.vendorCategory],
                'user_type': [this.user.user_type],
                'roleId': [this.user.roleId, Validators.required]
         });
         }

       })
   }

}
