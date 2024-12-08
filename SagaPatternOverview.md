# <p align="center"><strong>Saga Pattern</strong></p>

## Mục lục
1. [Bối cảnh](#context)
2. [Giải pháp](#solution)
3. [Phân loại](#type)
4. [Slide](#slide)
5. [Tài liệu tham khảo](#materials)

## Bối cảnh <a name="context"></a>
Transaction là một đơn vị logic hoặc công việc, đôi khi được tạo thành từ nhiều thao tác. Trong một transaction, một event là một sự thay đổi trạng thái xảy ra với một thực thể và một command sẽ đóng gói tất cả thông tin cần thiết để thực hiện một hành động hoặc kích hoạt một event sau đó.

Các transaction phải có các tính chất: atomic, consistent, isolated, and durable (ACID):
* **Atomicity** đề xuất một transaction làm tất cả hoặc không làm gì cả.
* **Consistency** đảm bảo rằng một transaction không bao giờ chấp nhận trạng thái không đồng nhất trong cơ sở dữ liệu.
* **Isolation** duy trì sự tách rời giữa các transaction cho đến khi chúng hoàn tất.
* **Durability** đảm bảo rằng cơ sở dữ liệu theo dõi các thay đổi một cách an toàn để máy chủ có thể khôi phục từ một kết thúc bất thường.

 Các ứng dụng monolithic truyền thống chủ yếu phụ thuộc vào các thuộc tính ACID để duy trì tính toàn vẹn dữ liệu. Tuy nhiên, khi các ứng dụng trở nên phức tạp hơn, nhược điểm của mô hình monolithic trở nên rõ ràng hơn. Trong khi kiến trúc microservices hiệu quả trong việc giải quyết nhiều hạn chế này, nó cũng mang lại một thách thức lớn trong việc quản lý transaction và đảm bảo tính nhất quán dữ liệu trên nhiều hệ thống database và service độc lập.

## Giải pháp <a name="solution"></a>
Mô hình Saga cung cấp khả năng quản lý transaction bằng cách sử dụng một chuỗi các **local transaction**. 
Một local transaction là một công việc nguyên tử được thực hiện bởi một service. Mỗi local transaction cập nhật cơ sở dữ liệu và gửi một message hoặc event để kích hoạt local transaction tiếp theo. Nếu một local transaction không thành công, saga sẽ thực hiện một chuỗi compensating transactions để hoàn tác các thay đổi được thực hiện bởi các local transactions trước đó.

Trong mô hình Saga:
* **Compensable transactions** là các transactions có khả năng bị đảo ngược bằng cách xử lý một transaction khác có tác động ngược lại.
* Một **pivot transaction** là go/no-go point trong mô hình saga. Nếu pivot transaction được cam kết, mô hình saga sẽ chạy cho đến khi hoàn thành. Một pivot transaction có thể là transaction không thể được đền bù cũng như không thể thử lại hoặc có thể là transaction có thể được đền bù cuối cùng hoặc transaction có thể thử lại đầu tiên trong saga.
* **Retryable transactions** là các transactions tuân theo pivot transaction và được đảm bảo thành công.

## Phân loại <a name="type"></a>
Có hai cách tiếp cận chính để triển khai Saga Pattern: **choreography** and **orchestration**. 
### Orchestration
### Choreography
 
## Slide <a name="slide"></a>
Truy cập slide tại [đây](https://docs.google.com/presentation/d/1QM-dJe-HjJbaqhcptWJrMSFpHKgohrZ471HvxtWJKqQ/edit?usp=sharing).

## Tài liệu tham khảo <a name="materials"></a>
1. [Saga Pattern - Azure](https://learn.microsoft.com/en-us/azure/architecture/reference-architectures/saga/saga)
2. [Distributed transaction - SAGA pattern](https://viblo.asia/p/distributed-transaction-saga-pattern-naQZRRnPZvx)
3. [Distributed transaction - Two-phase commit](https://viblo.asia/p/distributed-transaction-two-phase-commit-naQZRBemZvx)
4. [Giới thiệu về Saga Pattern trong microservices](https://duypt.dev/gioi-thieu-ve-saga-pattern-trong-microservices)
