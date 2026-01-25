
become a influencer process

1. become a influencer 버튼을 누르면 모달이 생김
2. 내 공식 INSTAGRAM으로 DM하라고 하기
 - DM 양식: 본인의 avatarbank 닉네임을 보내면서 인플루언서 요청을 하라

 그러면 내가 DM을 확인하고 적정성여부를 보고 Influencer로 올림
 Influencer로 올리는건 오직 관리자 계정만 가능하다. (관리자계정은 .env에서 관리리)


3. Influencer로 올라가면 
  - 네비바에 Influencer라고 표시가 됨 
  - 프로필 아이콘 클릭시 전용메뉴가 보임(4번)

4. Influencer 전용메뉴 
  본인이 원하는 사진 20~50장 정도를 올린 후, 학습요청 버튼 클릭
  내부적으로는 AWS S3에 저장된다. (경로는 알아서 따줘)

5. 내가 수동으로 그거 확인해서 학습시킨후 S3의 LORA/{ID} 폴더에 해당 인플루언서의 LORA를 넣는다. (한명당 여러개도 만들수있음)
   넣을때는 내 관리자용 화면에서 넣어야하며, 업로드 이후 메일발송 기능있어야함

6. Influencer는 메일확인 후 LORA에 대한 판매 옵션을 지정해서 저장한다. 
