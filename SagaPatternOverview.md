# <p align="center"><strong>Saga Pattern</strong></p>

## Mục lục
1. [Bối cảnh](#context)
2. [Giải pháp](#solution)
3. [Phân loại](#type)
4. [Slide](#slide)
5. [Một số lưu ý](#considerations)
6. [Khi nào nên sử dụng](#when_to_use)
7. [Tài liệu tham khảo](#materials)

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
![ảnh](https://learn.microsoft.com/en-us/azure/architecture/reference-architectures/saga/images/saga-overview.png)

Trong mô hình Saga:
* **Compensable transactions** là các transactions có khả năng bị đảo ngược bằng cách xử lý một transaction khác có tác động ngược lại.
* Một **pivot transaction** là go/no-go point trong mô hình saga. Nếu pivot transaction được cam kết, mô hình saga sẽ chạy cho đến khi hoàn thành. Một pivot transaction có thể là transaction không thể được đền bù cũng như không thể thử lại hoặc có thể là transaction có thể được đền bù cuối cùng hoặc transaction có thể thử lại đầu tiên trong saga.
* **Retryable transactions** là các transactions tuân theo pivot transaction và được đảm bảo thành công.

## Phân loại <a name="type"></a>
Có hai cách tiếp cận chính để triển khai Saga Pattern: **choreography** and **orchestration**. 
### Orchestration
#### Khái niệm
Trong mô hình Orchestration-Based Saga, một orchestrator (người điều phối) duy nhất sẽ quản lý tất cả các transaction và chỉ đạo các service thực hiện các local transactions.

Orchestrator hoạt động như một bộ điều khiển tập trung của tất cả các local transactions này, duy trì status của toàn bộ transaction và xử lý việc khắc phục lỗi bằng các compensable transactions.
![ảnh](https://learn.microsoft.com/en-us/azure/architecture/reference-architectures/saga/images/orchestrator.png)
#### Ưu điểm
* Phù hợp cho các quy trình làm việc phức tạp liên quan đến nhiều service cùng tham gia.
* Thích hợp khi có kiểm soát đối với từng service tham gia trong quy trình và kiểm soát đối với luồng hoạt động.
* Không tạo ra cyclic dependencies, vì orchestrator phụ thuộc một chiều vào các service tham gia của Saga.
* Các service tham gia không cần biết về các xử lý cũng như event của các service tham gia khác. Sự phân chia rõ ràng về mặt quan tâm giúp đơn giản hóa business logic.
#### Nhược điểm
* Phức tạp hóa thiết kế, yêu cầu triển khai thêm một logic orchestration.
* Có một point of failure bổ sung, vì orchestrator quản lý toàn bộ quy trình làm việc. Nếu orchestrator gặp sự cố thì toàn bộ quy trình đều ngừng hoạt động.
* Bottle neck/Letancy: khi số lượng services trong qua trình xử lý tăng lên cao thì rất dễ bottle neck.
* Design hệ thống không cẩn thận cũng rất dễ dính vào cái bẫy distributed monolithic application.
### Choreography
#### Khái niệm
Trong mô hình Choreography-Based Saga, tất cả các service tham gia vào transaction phân tán sẽ emit một event mới sau khi hoàn thành các local transactions của chúng.

Phương pháp Choreography-Based Saga không có orchestrator để chỉ đạo và thực hiện các local transactions. Thay vào đó, mỗi service sẽ chịu trách nhiệm tạo ra một event mới và nó sẽ kích hoạt transaction của service tiếp theo.
![ảnh](https://learn.microsoft.com/en-us/azure/architecture/reference-architectures/saga/images/choreography-pattern.png)
#### Ưu điểm
* Phù hợp cho các quy trình làm việc đơn giản yêu cầu ít bên tham gia và không cần logic điều phối.
* Không đòi hỏi triển khai và bảo trì dịch vụ bổ sung.
* Trách nhiệm được phân phối qua các bên tham gia của Saga, do đó không sinh ra point of failure.
#### Nhược điểm
* Quy trình làm việc có thể trở nên rối hơn khi thêm các step mới, đồng thời khó theo dõi được service nào của Saga đang lắng nghe sự kiện nào nào.
* Có rủi ro về cyclic dependencies giữa các bên tham gia của Saga vì chúng phải consume các message của nhau.
* Quy trình Kiểm thử tích hợp khó khăn vì tất cả các service phải đang chạy để mô phỏng một transaction.
* Ngoài ra việc các business logic phân tán ở nhiều chỗ khiến việc hiểu toàn bộ flow trở nên khó khăn hơn.
## Một số điểm lưu ý <a name="considerations"></a>
* Mô hình Saga có thể khá khó khăn ban đầu, vì nó đòi hỏi cách tư duy mới về cách phối hợp một transaction và duy trì tính nhất quán dữ liệu cho một business process bao gồm nhiều microservices.
* Mô hình Saga khó debug, và độ phức tạp tăng lên khi số lượng service tham gia tăng lên.
* Dữ liệu khó có thể được rollback khi mà các service tham gia của Saga commit các thay đổi vào local databases của chúng.
* Khi triển khai phải có khả năng xử lý một tập hợp các lỗi tạm thời có thể xảy ra và cung cấp tính đồng nhất để giảm thiểu các side effects và đảm bảo tính nhất quán dữ liệu.
* Đồng nhất có nghĩa là cùng một hoạt động có thể được lặp lại nhiều lần mà không làm thay đổi kết quả ban đầu.
* Nên triển khai observability để kiểm tra và theo dõi quy trình làm việc của Saga.
* Việc thiếu tính isolation của data của các service tham gia tạo ra thách thức về tính bền vững.
* Các hiện tượng bất thường sau có thể xảy ra nếu không có các biện pháp phòng ngừa thích hợp:
  * Lost updates - Mất cập nhật, khi một Saga ghi mà không đọc những thay đổi được thực hiện bởi một Saga khác.
  * Dirty reads - Đọc không an toàn, khi một giao dịch hoặc một Saga đọc các cập nhật được thực hiện bởi một Saga khác mà chưa hoàn thành những cập nhật đó.
  * Fuzzy/nonrepeatable reads - Đọc mơ hồ/không lặp lại, khi các step khác nhau của Saga đọc dữ liệu khác nhau vì có một thay đổi dữ liệu bất thường xảy ra ở giữa.
* Các biện pháp phòng ngừa để giảm thiểu hoặc ngăn chặn các hiện tượng bất thường bao gồm:
  * Semantic lock - Khóa ngữ nghĩa, một khóa cấp ứng dụng mà transaction có thể sử dụng để chỉ định một thay đổi đang diễn ra và chưa hoàn thành.
  * Commutative updates - Cập nhật giao hoán - có thể thực hiện theo bất kỳ thứ tự nào và tạo ra cùng một kết quả.
  * Pessimistic view - Quan điểm bi quan: Có khả năng một Saga đọc dữ liệu không an toàn trong khi Saga khác đang chạy một compensation để rollback.
  * Quan điểm bi quan sắp xếp lại Saga để cập nhật dữ liệu cơ bản trong một transaction có thể thử lại, loại bỏ khả năng dirty reads.
  * Reread value - Đọc lại giá trị - xác nhận rằng dữ liệu không thay đổi, sau đó cập nhật lại log. Nếu log đã thay đổi, các bước sẽ bị hủy bỏ và Saga có thể khởi động lại.
  * Tạo ra một tệp versioning ghi lại các thao tác trên một bản ghi khi chúng được yêu cầu, sau đó thực hiện theo đúng thứ tự.
  * Tuỳ theo giá trị yêu cầu mà lựa chọn các cơ chế xử lý concurrency phù hợp.

## Khi nào nên sử dụng <a name="when_to_use"></a>
* Đảm bảo tính nhất quán của dữ liệu trong hệ thống phân tán mà không có sự liên kết chặt chẽ.
* Khôi phục hoặc bù đắp nếu một trong các thao tác trong chuỗi không thành công.

## Slide <a name="slide"></a>
Truy cập slide tại [đây](https://docs.google.com/presentation/d/1QM-dJe-HjJbaqhcptWJrMSFpHKgohrZ471HvxtWJKqQ/edit?usp=sharing).

## Tài liệu tham khảo <a name="materials"></a>
1. [Saga Pattern - Azure](https://learn.microsoft.com/en-us/azure/architecture/reference-architectures/saga/saga)
2. [Distributed transaction - SAGA pattern](https://viblo.asia/p/distributed-transaction-saga-pattern-naQZRRnPZvx)
3. [Distributed transaction - Two-phase commit](https://viblo.asia/p/distributed-transaction-two-phase-commit-naQZRBemZvx)
4. [Giới thiệu về Saga Pattern trong microservices](https://duypt.dev/gioi-thieu-ve-saga-pattern-trong-microservices)
