import { Component, OnInit } from '@angular/core';
import {FormBuilder, FormGroup, Validators} from "@angular/forms";
declare var jQuery: any;
import {  GlobalsService } from 'app/services';
import { GetValidimageTypes} from 'app/parameters';
import {Router} from "@angular/router";
import {RedConstants} from "app/classes/constants";
import {FeedbackService} from "./feedback.service";

@Component({
  selector: 'app-partner-feedback',
  templateUrl: './partner-feedback.component.html',
  styleUrls: ['./partner-feedback.component.scss']
})
export class PartnerFeedbackComponent implements OnInit {
  private feedbackForm:FormGroup
  private attachementFileDetails:File
  private attachementErrorMsg:string
  private attachementFilename:string
  private feedbackOption:any
  constructor(private fb: FormBuilder,private router: Router,private feedback_service:FeedbackService,private gs: GlobalsService) { }


  ngOnInit() {
    this.feedbackForm = this.fb.group({
      'reason': ['',[Validators.required]],
      'name': ['',[Validators.required]],
      'email': ['',[Validators.required,Validators.pattern(/^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/)]],
      'mobile': ['',[Validators.required,Validators.pattern(/^(\+91-|\+91|0)?\d{10}$/)]],
      'description': ['',[Validators.required]],
      'attachments': ['']
    })
    this.feedbackOption = RedConstants.FEEDBACK_OPTION
  }
  private openAttachment(event){
    event.preventDefault();
    jQuery('#fileId').click();
  }
  private uploadAttchementFile(event: EventTarget){
    let eventObj: MSInputMethodContext = <MSInputMethodContext> event;
    let target: HTMLInputElement = <HTMLInputElement> eventObj.target;
    let files: FileList = target.files;
    let attachementFiles=files[0];
    let filename = attachementFiles.name;
    let fileType=attachementFiles.type;
    let validImageTypes =GetValidimageTypes();
    if (jQuery.inArray(fileType,validImageTypes.validType)==-1) {
      this.attachementErrorMsg='Upload valid formats'
      this.attachementFilename=null
    }
    else {
      this.attachementErrorMsg = null
      this.attachementFileDetails = attachementFiles;
      this.attachementFilename = filename;
    }

  }
  private addFeedBack(formvalues){
    if(this.attachementErrorMsg==null || typeof this.attachementFileDetails=='undefined'){
      this.feedback_service.createFeedback(formvalues,this.attachementFileDetails)
          .then(data=>{
            this.gs.setToastMessage('Thank you! our representative will update you shortly ', 3000);
              this.router.navigate(['/app/dashboard']);
          })
    }

  }

  private openUploadFile(event){
    event.preventDefault();
    jQuery('#filenameId').click();
  }
  private openImageFile(event){
    event.preventDefault();
    jQuery('#imagefileId').click();
  }
  private openTermsconditionFile(event){
    event.preventDefault();
    jQuery('#fileId').click();

  }


}
