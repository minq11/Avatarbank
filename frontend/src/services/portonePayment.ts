/**
 * 포트원(PortOne V2) 결제창 열기.
 *
 * SDK 는 index.html 에서 전역으로 로드한다 (window.PortOne).
 * 서버가 확정한 주문(금액·paymentId)을 그대로 넘기는 게 핵심이다 —
 * 프론트에서 금액을 계산해 넘기면 위변조 여지가 생긴다.
 *
 * 결제창이 끝나면 서버가 /payments/portone/complete 에서 포트원에 직접 조회해
 * 금액과 상태를 검증한 뒤에만 크레딧을 적립한다. 이 프론트 코드가 성공이라고
 * 말하는 것만으로는 아무것도 적립되지 않는다.
 */

import type { CreditOrder } from "./api";
import { creditsApi } from "./api";

interface PortOneRequestPaymentResponse {
  paymentId?: string;
  /** 존재하면 결제 실패. 포트원은 성공/실패를 이 필드 유무로 구분한다. */
  code?: string;
  message?: string;
  pgCode?: string;
  pgMessage?: string;
}

declare global {
  interface Window {
    PortOne?: {
      requestPayment: (
        options: Record<string, unknown>
      ) => Promise<PortOneRequestPaymentResponse | undefined>;
    };
  }
}

export async function openPortOnePayment(order: CreditOrder): Promise<void> {
  if (!window.PortOne) {
    throw new Error("결제 모듈을 불러오지 못했어요. 새로고침 후 다시 시도해 주세요.");
  }
  if (!order.store_id || !order.channel_key) {
    throw new Error("결제가 아직 설정되지 않았어요.");
  }

  try {
    const response = await window.PortOne.requestPayment({
      storeId: order.store_id,
      channelKey: order.channel_key,
      // 서버가 만든 주문번호를 그대로 paymentId 로 쓴다. 같은 paymentId 로
      // 여러 번 시도할 수 있지만 최종 성공은 한 번뿐이다 (포트원이 중복 결제를 막는다).
      paymentId: order.order_id,
      orderName: order.order_name,
      totalAmount: order.amount_krw,
      currency: "CURRENCY_KRW",
      // 카카오페이는 PG 사 자체가 간편결제사라 EASY_PAY 로 지정한다.
      // easyPayProvider 는 채우지 않아도 되고, 채워도 무시된다.
      payMethod: "EASY_PAY",
      // 모바일에서는 리다이렉트가 강제된다. redirectUrl 을 주지 않으면
      // 모바일 결제 UI 가 제대로 뜨지 않으므로 반드시 넘긴다.
      // forceRedirect 는 주지 않는다 — PC 는 반환값, 모바일은 리다이렉트로
      // 각 환경에 맞는 흐름을 쓰기 위해서다. 그래서 아래 두 경로를 모두 처리한다.
      redirectUrl: order.redirect_url,
    });

    // 리다이렉트로 처리된 경우 여기 도달하지 않는다 (페이지가 이미 떠났다).
    // 반환값 방식일 때만 아래가 실행된다.
    // 실패를 예외로 바꿔 아래 catch 가 대기 주문 정리를 한 곳에서 처리하게 한다.
    if (response?.code !== undefined) {
      throw new Error(response.message || "결제가 취소되었어요.");
    }
  } catch (e) {
    // 사용자가 결제창을 닫았거나 PG 가 거절했거나 SDK 가 던진 경우.
    // 대기 중인 주문을 정리해 두지 않으면 pending 주문이 계속 쌓인다.
    // 정리 실패는 치명적이지 않으므로 삼킨다.
    void creditsApi.cancelOrder(order.order_id).catch(() => undefined);
    throw e;
  }
}
