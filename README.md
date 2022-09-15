# 주문, 배송, 쿠폰 관리 API
원티드 프리온보딩 백엔드 기업 과제

## 목차
1. [프로젝트 개요](#프로젝트-개요)
2. [과제 요구사항 분석](#과제-요구사항-분석)
3. [프로젝트 기술 스택](#프로젝트-기술-스택)
4. [개발 기간](#개발-기간)
5. [ERD](#erd)
6. [API 목록](#api-목록)
7. [프로젝트 시작 방법](#프로젝트-시작-방법)


<br>


## 프로젝트 개요


Django Rest Framework 를 이용한 REST API 서버로

- 주문 내역 전체 조회(필터링, 검색), 상세 조회, 수정 
- 쿠폰 타입 생성, 전체 조회, 상세 조회, 수정, 삭제 기능
- 쿠폰 생성, 전체 조회, 상세 조회, 수정, 삭제 기능
- 테스트를 위한 주문 내역 생성, 조회 기능

위 기능을 제공합니다.

<br>

## 과제 요구사항 분석


### 1. 주문 내역 관련

#### 1) 주문 내역 전체 조회

- 주문 내역 조회시 주문 날짜, 결제 상태, 배송 상태로 필터링 가능

    - 필터링시 `django-rest-framework` `genericViewSet`의 `get_queryset` 함수를 오버라이드하여 구현
  
    <br>
  
- 주문 내역시 주문자 id로 검색 가능

    - `django-rest-framework`의 `Searchfilter` 사용
    - 주문자명으로 검색 가능하도록 수정 예정
  
#### 2) 주문 내역 수정
- 주문 내역의 결제 상태, 배송 상태 수정 가능
- 결제 취소 처리시 사용한 쿠폰은 복구 처리


### 2. 쿠폰 관련
#### 2-1) 쿠폰 타입
- 쿠폰 타입은 아래와 같은 값을 가지게 됨

    - 유효 기간(시작, 종료, 기한)
    - 최소 주문 금액
    - 최대 할인 금액(% 할인의 경우)
    - 할인 종류(배송비, 비율, 정액 할인)
    - 발급 종류(관리자 지정, 사용자 직접, 자동 발급)
    - 값(할인 금액, 비율)
    - 설명
    - 쿠폰 코드
    - 활성화(관련 쿠폰 발급 가능/불가능)
 <br>


- 쿠폰 코드의 경우 사용자 직접 발급 받는 종류일 때만 쿠폰 타입 생성시 지정
- 관리자 지정 혹은 자동 발급인 경우 쿠폰을 발급할 때 코드 생성

#### 2-2) 쿠폰

- 쿠폰 발급할 때 쿠폰 타입 id와 유저 id 필요
- 모든 발급한 쿠폰 조회 가능

#### 2-3) 쿠폰 사용 내역

- 쿠폰 타입별 사용 횟수, 발급 횟수,  총 할인액 조회 가능

### 3. 테스트 관련

#### 3-1) 테스트를 위한 구매 내역 생성 API
- 쿠폰 사용에 따른 사용 할인 적용
- 구매 국가, 구매 갯수에 따른 배송비 적용
- 수출입은행 API를 이용해 현재 원-달러 환율을 가져와서 배송비를 적용
    
#### 3-2) 테스트

- 주문 (쿠폰 적용) 테스트 <br>
    - 성공
    - 실패: 주문 금액이 쿠폰 사용 조건인 최소 주문 금액보다 적은 경우
    - 실패: 쿠폰이 만료된 경우

![image](https://user-images.githubusercontent.com/55697800/190423920-4282600b-b0ad-44a0-afb9-af87bce79e0d.png)

<br>

- 쿠폰 타입 테스트 <br>
    - 성공
    - 실패: 퍼센트 할인 쿠폰의 값이 100 초과
    - 실패: 유효 기간 종료 날짜가 시작 날짜 보다 이전인 경우
    - 실패: 유효 기간 종료 날짜가 현재 보다 이전인 경우

- 쿠폰 생성 테스트 <br>
    - 성공
    - 실패: 쿠폰 타입 만료(유효기간 지남)
    - 실패: 비활성화 상태(`is_active=False`)인 쿠폰 타입


![image](https://user-images.githubusercontent.com/55697800/190436120-ab3c0671-aabf-44ed-a0c9-53f6426c4351.png)


<br>


### 4. 특이사항

- 실시간 환율 API(한국수출입은행)를 통해 원-달러 환율을 받아오게 되는데 일일 호출 횟수 제한이 있음
  - 하루 한 번 환율을 저장한 `%Y-%m-%d.json` 파일 생성
- 국가별 개수별 배송비 데이터와 국가명-코드 데이터는 `apps/data/` 디렉터리에 `json` 형태로 저장 후 접근

<br>

### 기능 목록

| 버전   | 기능         | 세부 기능 | 설명                                 | 상태  |
|------|------------|-------|------------------------------------|-----|
| v1   | 주문 내역      | 조회    | 주문 내역 조회시 필터링, 검색 가능               | ✅   |
| -    | -          | 수정    | 결제상태, 배송상태 수정 가능하며 결제 상태 수정시 쿠폰 리셋 | ✅   |
| -    | 쿠폰 타입      | 생성    | 쿠폰 타입 생성                           | ✅   |
| -    | -          | 조회    | 쿠폰 타입 조회                           | ✅   |
| -    | -          | 수정    | 쿠폰 타입 수정                           | ✅   | 
| -    | -          | 삭제    | 쿠폰 타입 삭제                           | ✅   |
| -    | 쿠폰         | 생성    | 쿠폰 생성                              | ✅   |
| -    | -          | 조회    | 쿠폰 조회                              | ✅   |
| -    | -          | 수정    | 쿠폰 수정                              | ✅   | 
| -    | -          | 삭제    | 쿠폰 삭제                              | ✅   |
| -    | -          | 조회    | 쿠폰 사용 내역 통계                        | ✅   |
| -    | (테스트)주문 내역 | 생성    | 쿠폰 및 국가별 배송비, 환율 적용한 주문 내역 생성      | ✅   |
| -    | 테스트        | 테스트   | 기능, 전체 테스트                             | ✅   |

🔥 추가 기능 구현시 업데이트 예정

<br>

## 프로젝트 기술 스택



### Backend
<section>
<img src="https://img.shields.io/badge/Django-092E20?logo=Django&logoColor=white"/>
<img src="https://img.shields.io/badge/Django%20REST%20Framework-092E20?logo=Django&logoColor=white"/>
</section>

### DB
<section>
<img src="https://img.shields.io/badge/MySQL-4479A1?logo=MySQL&logoColor=white"/>
</section>

### Tools
<section>
<img src="https://img.shields.io/badge/GitHub-181717?logo=GitHub&logoColor=white"/>
<img src="https://img.shields.io/badge/Discord-5865F2?logo=Discord&logoColor=white">
<img src="https://img.shields.io/badge/Postman-FF6C37?logo=Postman&logoColor=white">
</section>


<br>


## 개발 기간


- 2022/09/08, 09/13 - 14 (3일)


<br>


## ERD
ERD 

![](http://drive.google.com/uc?export=view&id=1PwWcObGK2Cj0fbAXEJKjPR2iYJABwn8_)


<br>


## API 목록
API 명세 주소

[POSTMAN API Document](https://documenter.getpostman.com/view/19274775/2s7YfHix7q)

<br>


## 프로젝트 시작 방법
1. 로컬에서 실행할 경우
```bash
# 프로젝트 clone(로컬로 내려받기)
git clone -b develop --single-branch ${github 주소}
cd ${디렉터리 명}

# 가상환경 설정
python -m venv ${가상환경명}
source ${가상환경명}/bin/activate
# window (2 ways) 
# 1> ${가상환경명}/Scripts/activate
# 2> activate

# 라이브러리 설치
pip install -r requirements.txt
# 실행
python manage.py runserver
```

<br>
